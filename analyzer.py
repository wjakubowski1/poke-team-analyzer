import requests
from rich.console import Console

# init console
console = Console()

def fetch_pokemon(pokemon_name):
    # clean input and ensure lowercase
    name = pokemon_name.lower().strip()
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    
    # fetching animation
    with console.status(f"fetching: [bold green]{name}[/]...", spinner="dots"):
        response = requests.get(url)
        
    # check if ok
    if response.status_code == 200:
        data = response.json()
        
        # extract basic data
        pkmn_name = data["name"]
        types = [t["type"]["name"] for t in data["types"]]
        
        # print success output
        console.print(f"\n[bold cyan]✓ found:[/bold cyan] [bold white]{pkmn_name}[/bold white]")
        console.print(f"   [yellow]types:[/yellow] {', '.join(types)}")
        
    # check if not found
    elif response.status_code == 404:
        console.print(f"\n[bold red]✗ error:[/bold red] pokemon '{name}' not found")
    else:
        console.print(f"\n[bold red]✗ server error:[/bold red] code {response.status_code}")

if __name__ == "__main__":
    console.print("[bold magenta]--- cli pokedex v0.1 ---[/bold magenta]\n")

    # test valid names
    fetch_pokemon("gengar")
    fetch_pokemon("lucario")
    
    # test invalid name
    fetch_pokemon("pikachuuuu")