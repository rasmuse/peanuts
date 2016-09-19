import click
import time
import csv

PROPERTY_NAMES = ["Salt","Knaprig","Rostad","Flottig"]
NUM_PEANUTS = 20
TBF_CHOICES = ['APK', 'KFB'] + ['A{:2}'.format(i) for i in range(30)]

COLUMNS = (
    ["Timestamp","Din TBF","Vilken jordnöt?"]
    + PROPERTY_NAMES
    + ["Betygsätt totalupplevelsen","Kommentar"])

def create_file(path):
    with open(path, 'x') as f:
        w = csv.writer(
            f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(COLUMNS)

def save(path, tbf, peanut, score, properties, comment):
    row = (
        [time.strftime('%Y-%m-%d %H:%M:%S %z'), tbf, peanut]
        + [properties[key] for key in PROPERTY_NAMES]
        + [score, comment])
    with open(path, 'a') as f:
        w = csv.writer(
            f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(row)
        return True

def get_TBF():
    value = None
    error = None
    while True:
        if error:
            click.echo(error)
            error = None
        value = click.prompt('TBF', type=str)
        value = value.upper()
        if value in TBF_CHOICES:
            break
        else:
            error = '"{}" är inte en godkänd TBF'.format(value)
    return value


def ask_integer(q, min_=1, max_=7):
    value = None
    while True:
        value = click.prompt('{} [{}-{}]'.format(q, min_, max_), type=int)
        if min_ <= value <= max_:
            return value

def space_pad_right(s, l):
    l0 = len(s)
    return s + ' ' * (l - l0)

def ask_confirm():
    value = None
    while True:
        value = click.prompt('Spara detta svar? [j/n] ', prompt_suffix='', type=str)
        if value[0].lower() in ['j', 'y']:
            return True
        elif value[0].lower() in ['n']:
            return False


def collect_item():
    click.echo('BETYGSSÄTT EN JORDNÖT')
    click.echo('')

    person_id = get_TBF()
    peanut_id = ask_integer('Jordnöt', 1, NUM_PEANUTS)

    click.echo('')
    click.echo('Din åsikt')
    click.echo('------------------')
    score = ask_integer('Betygssätt totalupplevelsen', 1, 7)

    click.echo('')
    click.echo('Beskriv jordnöten')
    click.echo('------------------')

    properties = {}
    for k in PROPERTY_NAMES:
        properties[k] = ask_integer(k, 1, 7)

    comment = click.prompt('Kommentar', type=str, default='')


    def echo_item(label, value):
        click.echo('{} {}'.format(space_pad_right(label + ':', 11), value))

    click.echo('')
    click.echo('Bekräfta uppgifter')
    click.echo('------------------')
    
    echo_item('Din TBF', person_id)
    echo_item('Jordnöt', peanut_id)
    echo_item('Betyg', score)
    for k in PROPERTY_NAMES:
        echo_item(k, properties[k])
    echo_item('Kommentar', comment)

    click.echo('')
    if ask_confirm():
        return (person_id, 'J{}'.format(peanut_id), score, properties, comment)
    else:
        raise click.Abort()
    


@click.command()
@click.argument('path', type=click.Path(exists=False))
def collect_data(path):
    create_file(path)
    while True:
        try:
            item = collect_item()
            if save(path, *item):
                click.echo('Sparat!')
            exit_status = ''
        except click.Abort:
            exit_status = 'Avbruten!'
        
        try:
            click.echo(exit_status)
            click.confirm('Tryck ENTER för att mata in ny jordnöt.', default=True, prompt_suffix='', show_default=False)
        except click.Abort:
            pass

        click.clear()



if __name__ == '__main__':
    collect_data()