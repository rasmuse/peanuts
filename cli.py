import time
import csv
import click
import prompt_toolkit
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.shortcuts import create_prompt_application
from prompt_toolkit.shortcuts import create_eventloop
from prompt_toolkit.shortcuts import create_prompt_layout
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.token import Token
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.filters import Condition, Filter
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict

style = style_from_dict({
    Token.Toolbar: '#333333 bg:#cccccc',
})

prompt_toolkit.key_binding.manager.KeyBindingManager(
    registry=None, enable_vi_mode=None, get_search_state=None,
    enable_abort_and_exit_bindings=False, enable_system_bindings=False,
    enable_search=False, enable_open_in_editor=False,
    enable_extra_page_navigation=False, enable_auto_suggest_bindings=False,
    enable_all=True)

TBF_VALUES = ['a', 'c']
N_PEANUTS = 20
PROPERTY_NAMES = ['Salt', 'Knaprig', 'Rostad', 'Flottig']

COLUMNS = (
    ["Timestamp","Din TBF","Vilken jordnöt?"]
    + PROPERTY_NAMES
    + ["Betygsätt totalupplevelsen","Kommentar"])

CSV_SETTINGS = dict(delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
def create_file(path):
    with open(path, 'x') as f:
        w = csv.writer(f, **CSV_SETTINGS)
        w.writerow(COLUMNS)

def save(path, item):
    item['Timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S %z')
    row = [item[k] for k in COLUMNS]
    with open(path, 'a') as f:
        w = csv.writer(f, **CSV_SETTINGS)
        w.writerow(row)

class Restart(Exception): pass

class NumberValidator(Validator):
    def __init__(self, min_, max_):
        self._min = min_
        self._max = max_

    def validate(self, document):
        text = document.text

        i = 0
        if text.isdigit():
            if self._min <= int(text) <= self._max:
                return
        else:
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

        raise ValidationError(
            message='Mata in ett tal ({}-{})'.format(self._min, self._max),
            cursor_position=i)

class SetValidator(Validator):
    def __init__(self, values):
        self._values = set(values)

    def validate(self, document):
        text = document.text

        if text not in self._values:
            raise ValidationError(
                message='Otillåtet värde',
                cursor_position=len(text))

@click.command()
@click.argument('path', type=click.Path(exists=False))
def main(path):
    create_file(path)

    progression = [
        ('asking', 'TBF'),
        ('asking', 'Vilken jordnöt'),
        ('asking', 'Salt'),
    ]
    context = {'items': []}
    def get_state():
        return context['current']
    def set_state(s):
        context['current'] = s

    mgr = KeyBindingManager(enable_abort_and_exit_bindings=True)

    def prompt_tokens(cli):
        state = get_state()
        if state[0] == 'asking':
            return [
                (Token, state[1]),
                (Token.Colon, ':'),
                (Token.Space, ' ')
                ]
        if state[0] == 'canceling':
            return [(Token, 'Avbryt? (j/n) ')]

        raise RuntimeError(state)

    def get_toolbar_tokens(cli):
        return [(Token.Toolbar, 'Ctrl+C: Avbryt')]

    @Condition
    def is_canceling(cli):
        return get_state()[0] == 'canceling'

    @mgr.registry.add_binding('j', filter=is_canceling)
    def _(event):
        raise Restart()


    @mgr.registry.add_binding('n', filter=is_canceling)
    def _(event):
        previous_state = get_state()[1]
        set_state(previous_state)
        event.cli.current_buffer.undo()


    @mgr.registry.add_binding(Keys.ControlC)
    def _(event):
        event.cli.current_buffer.save_to_undo_stack()
        event.cli.current_buffer.cursor_position = 0
        event.cli.current_buffer.text = ''
        set_state(('canceling', get_state()))


    things = (
        [
        'NY JORDNÖT\n==============\n',
        {'key': "Din TBF", 'v': SetValidator(TBF_VALUES)},
        {'key': "Vilken jordnöt?", 'v': NumberValidator(1, N_PEANUTS)},
        '\n\nDin åsikt\n-----------------\n',
        {'key': "Betygsätt totalupplevelsen", 'v': NumberValidator(1, 7)},
        '\n\nBeskriv jordnöten\n-----------------\n',
        ]
        +
        [{'key': n, 'v': NumberValidator(1, 7)} for n in PROPERTY_NAMES]
        +
        [{'key': "Kommentar", 'v': None}]
        )
    
    while True:
        try:
            clear()
            item = {}
            for t in things:
                if isinstance(t, str):
                    print(t)
                    continue

                k, validator = t['key'], t['v']
                set_state(('asking', k))
                inp = prompt(
                    get_prompt_tokens=prompt_tokens,
                    get_bottom_toolbar_tokens=get_toolbar_tokens,
                    key_bindings_registry=mgr.registry,
                    style=style,
                    validator=validator
                    )
                item[k] = inp
            save(path, item)
        except Restart:
            pass
            
    

if __name__ == '__main__':
    main()