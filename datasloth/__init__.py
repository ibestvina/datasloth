import os
import inspect
import re
import pandas as pd
from pandas.api.extensions import register_dataframe_accessor
from pandas.api.types import is_string_dtype, is_numeric_dtype, is_datetime64_any_dtype
from sqlalchemy import desc
from pandasql import sqldf, PandaSQLException
import openai


@pd.api.extensions.register_dataframe_accessor("sloth")
class SlothAccessor:
    """
    Pandas Dataframe accessor to add '.sloth.description' field to dataframes,
    and manage column summaries used by DataSloth.
    """
    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._validate(pandas_obj)
        self._obj = pandas_obj
        self._description = '{COLUMNS_SUMMARY}'

    @staticmethod
    def _validate(obj):
        pass

    @property
    def description(self) -> str:
        return self._description.format(COLUMNS_SUMMARY=self.columns_summary())

    @description.setter
    def description(self, value: str) -> None:
        """
        Set additional description manually to inform the language engine about this table.
        Use '{COLUMNS_SUMMARY}' to include the default column summary in the description.
        By default, description is set only to this summary. To reset it, set description to None.
        """
        if value is None:
            self._description = '{COLUMNS_SUMMARY}'
        else:
            self._description = value
    
    def columns_summary(self) -> str:
        """
        Returns columns summary of the dataframe, in the "table" format containing
        column names, data types and additional info about columns.
        """
        summary_lines = ['|column name|data type|info|']
        for col_name in self._obj:
            col = self._obj[col_name]
            summary_lines.append(f'|{col_name}|{col.dtype}|{column_info(col)}|')
        return '\n'.join(summary_lines)
        
    
class DataSloth():
    prompt_format = """

Make sure to join in tables if information from multiple tables is needed for a task.

Task: percentage of True values of column X in table Y
```
SQL query for SQLite:
SELECT (SUM(CASE WHEN X = 'True' THEN 1.0 END) / COUNT(*)) * 100 AS percentage
FROM Y
```

Task: count of rows in table T where date is equal to 11th of August 1993
```
SQL query for SQLite:
SELECT COUNT(*) AS row_count
FROM T
WHERE date(date) = date('1993-08-11')
```

Task: {QUERY}
SQL query for SQLite:
```
"""

    def __init__(self, openai_api_key=None) -> None:
        if openai_api_key:
            openai.api_key = openai_api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise Exception(
                "OpenAI API key is not set. Either provide it to DataSloth(openai_api_key='...') "\
                "run openai.api_key('...'), or set it as an env variable OPENAI_API_KEY."
            )
        self.last_prompt = None
        self.last_gpt_response = None

    @staticmethod
    def dataframes_summary(env=None, ignore='^_'):
        summary_lines = ['Tables available in the database, with their additional information, are:']
        table_count = 0
        for name, value in env.items():
            if isinstance(value, pd.DataFrame) and (not ignore or not re.match(ignore, name)):
                summary_lines += [
                    f"\n\nTable name: {name}",
                    value.sloth.description
                ]
                table_count += 1
        if not table_count:
            return None
        return '\n'.join(summary_lines)

    def query(self, query, env=None, show_query=False):
        env = env or get_outer_frame_variables()
        query = query[0].lower() + query[1:]
        prompt = self.dataframes_summary(env)
        if not prompt:
            print('No dataframes found')
            return
        prompt += DataSloth.prompt_format.format(QUERY=query)
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n```\n"]
        )
        sql_query = response['choices'][0]['text']
        sql_query = sql_query.replace('```', '')
        self.last_prompt = (prompt, sql_query)
        if show_query:
            print(sql_query)
        try:
            result = sqldf(sql_query, env)
        except PandaSQLException:
            result = None
            print('Unsuccessful. Try rephrasing your query, or add additional table descriptions in df.sloth.description.')
            print('You can inspect the generated prompt and GPT response in sloth.show_last_prompt().')
        return result

    def generate(self, description, columns, n_rows=10):
        """
        Generates a random dataset based on the description and a list of columns.
        """

        rows = []
        while len(rows) < n_rows:
            prompt = f'Fill the table below with {min(n_rows - len(rows) + 5, 30)} random rows about {description}\n\n'
            prompt += f"|{'|'.join(columns)}|\n"
            prompt += f"|{'|'.join(['-'*len(col) for col in columns])}|\n|"
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=prompt,
                temperature=0.8,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            response = '|' + response['choices'][0]['text']
            new_rows = [row[1:-1].split('|') for row in response.split('\n') if not re.match('^[- |]*$', row)]
            new_rows = [row for row in new_rows if len(row) == len(columns)]
            rows += new_rows
            prompt = response + prompt

        df = pd.DataFrame(rows, columns=columns).head(n_rows)
        return df

    
    def _last_prompt(self):
        if self.last_prompt:
            print(self.last_prompt[0])
            print(f'[->]\n{self.last_prompt[1]}')

    def show_last_query(self):
        if self.last_prompt:
            print(self.last_prompt[1])

# Code copied from pandasql
def get_outer_frame_variables():
    """ Get a dict of local and global variables of the first outer frame from another file. """
    cur_filename = inspect.getframeinfo(inspect.currentframe()).filename
    outer_frame = next(f
                       for f in inspect.getouterframes(inspect.currentframe())
                       if f.filename != cur_filename)
    variables = {}
    variables.update(outer_frame.frame.f_globals)
    variables.update(outer_frame.frame.f_locals)
    return variables

def column_info(col):
    if is_string_dtype(col) or col.dtype == 'category':
        unique = col.unique().tolist()
        summary = 'unique values: ' + ', '.join(map(str, unique[:30]))
        if len(unique) > 30:
            summary += '...'
    elif col.dtype == 'bool':
        summary = f"values: 0, 1"
    elif is_numeric_dtype(col):
        summary = f"min={col.min()}, max={col.max()}"
    elif is_datetime64_any_dtype(col):
        summary = f"first={col.min()}, last={col.max()}"
    else:
        summary = ''
    return summary
