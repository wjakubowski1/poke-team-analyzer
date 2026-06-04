import requests
from rich.console import Console
from rich.table import Table

# init console
console = Console()

def get_pokemon_data(pokemon_name):
    # clean input
    name = pokemon_name.lower().strip()
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    
    with console.status(f"fetching {name}...", spinner="dots"):
        response = requests.get(url)
        
    if response.status_code == 200:
        data = response.json()
        
        # extract types
        types = [t["type"]["name"] for t in data["types"]]
        
        # extract base stats into a dictionary
        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        
        return {"name": data["name"], "types": types, "stats": stats}
    return None

def build_team():
    team = []
    console.print("\n[bold cyan]--- team builder (max 6) ---[/bold cyan]")
    console.print("type 'done' to finish or 'quit' to exit.\n")
    
    while len(team) < 6:
        user_input = console.input(f"slot {len(team) + 1}/6 - enter pokemon: ").lower().strip()
        
        if user_input in ['done', 'quit']:
            break
        if not user_input:
            continue
            
        pkmn_data = get_pokemon_data(user_input)
        
        if pkmn_data:
            team.append(pkmn_data)
            console.print(f"[green]✓ added {pkmn_data['name']} to team[/green]\n")
        else:
            console.print(f"[red]✗ error: pokemon '{user_input}' not found[/red]\n")
            
    return team

def display_team(team):
    if not team:
        console.print("[yellow]team is empty. exiting.[/yellow]")
        return
        
    # setup rich table
    table = Table(title="\ncurrent team roster", show_header=True, header_style="bold magenta")
    table.add_column("name", style="cyan")
    table.add_column("types", style="yellow")
    table.add_column("hp")
    table.add_column("atk")
    table.add_column("def")
    table.add_column("spd")
    
    # populate table with data
    for p in team:
        types_str = ", ".join(p["types"])
        stats = p["stats"]
        table.add_row(
            p["name"], 
            types_str, 
            str(stats["hp"]), 
            str(stats["attack"]), 
            str(stats["defense"]), 
            str(stats["speed"])
        )
        
    console.print(table)

if __name__ == "__main__":
    my_team = build_team()
    display_team(my_team)