<p align="center">
  <img width="300" src="https://raw.githubusercontent.com/ibestvina/datasloth/main/media/datasloth.png">
</p>

# DataSloth
_Natural language Pandas queries and data generation powered by GPT-3_


<p align="center">
  <img width="800" src="https://raw.githubusercontent.com/ibestvina/datasloth/main/media/quick_example.png">
</p>


## Installation
`pip install datasloth`

## Usage

In order for DataSloth to work, you must have a working [OpenAI API key](https://beta.openai.com/account/api-keys) set in your environment variable, or provide it to the DataSloth object. For more info, refer to this [guide](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).

DataSloth automatically discovers all Pandas dataframes in your namespace (filtering out names starting with an underscode). Before you load any data, import DataSloth and create the `sloth`:

```python
from datasloth import DataSloth
sloth = DataSloth()
```

Next, load any data you want to use. Try naming your dataframes and columns in a meaningful way, as DataSloth uses these names to understand what the data is about.

Once your data is loaded, simply run

`sloth.query('...')`

to query the data.


### Improving results

To improve the results, you can set custom descriptions of your tables:

`df.sloth.description = 'Verbose description of the table'`

By default, table descriptions consist of information about each column in the table. You can include this default description in your custom one by adding a `{COLUMNS_SUMMARY}` placeholder. See the detailed example notebook in the examples folder for more information.

### Solving issues

A lot of times, if the returned data is not correct, or not fully formatted the way you want, it helps to rephrase the question or give specific pointers to how the final data should look like. To better understand where things might have gone wrong, use `show_query=True` in the `sloth.query()`, or run `sloth.show_last_query()` after the prompt has finished to print out the SQL query used (whithout rerunning the engine).

## Data generation

DataSloth is also able to generate random data with the `generate` function. For example, running:
```python
sloth.generate(
    description="people from Mars, with very space-sounding names, and strange taste in ice cream", 
    columns=['First Name', 'Last Name', 'Date Of Birth', 'Country', 'City', 'Favourite Ice Cream'],
    n_rows=15
)
```
Produces something like this:
| First Name | Last Name | Date Of Birth | Country |             City | Favourite Ice Cream |
|-----------:|----------:|--------------:|--------:|-----------------:|--------------------:|
|     Glorza |    Mangal |    06/12/2079 |    Mars |      Pryus Mater |   Celestial Delight |
|      Yalza |     Krang |    09/21/2084 |    Mars | Valles Marineris |           Moon Mist |
|     Tralza |     Vomar |    04/17/2074 |    Mars |     Syrtis Major |        Mars Mud Pie |
|      Dalza |     Ralad |    01/02/2088 |    Mars |  Hellas Planitia |     Alien Abduction |
|      Halza |     Wular |    11/04/2092 |    Mars |     Olympus Mons |     Martian Sunrise |

Note that the results of the `generate` function are random, and different on each call.
