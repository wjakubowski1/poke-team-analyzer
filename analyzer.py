import requests
from rich.console import Console
from rich.table import Table

# init console
console = Console()

# cache for api calls to speed things up
type_cache = {}

def get_type_data(type_name):
    if type_name in type_cache:
        return type_cache[type_name]
    
    url = f"https://pokeapi.co/api/v2/type/{type_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["damage_relations"]
        type_cache[type_name] = data
        return data
    return None

def get_pokemon_data(pokemon_name):
    name = pokemon_name.lower().strip()
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    
    with console.status(f"fetching {name}...", spinner="dots"):
        response = requests.get(url)
        
    if response.status_code == 200:
        data = response.json()
        types = [t["type"]["name"] for t in data["types"]]
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
        
    table = Table(title="\ncurrent team roster", show_header=True, header_style="bold magenta")
    table.add_column("name", style="cyan")
    table.add_column("types", style="yellow")
    table.add_column("hp")
    table.add_column("atk")
    table.add_column("def")
    table.add_column("spd")
    
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

def analyze_weaknesses(team):
    if not team:
        return
        
    console.print("\n[bold cyan]--- team weakness analysis ---[/bold cyan]")
    
    weaknesses_count = {}
    
    with console.status("analyzing type matchups...", spinner="dots"):
        for p in team:
            pkmn_weaknesses = set()
            for t in p["types"]:
                type_data = get_type_data(t)
                if type_data:
                    # simplified: just looking at raw double damage from
                    for weak_to in type_data["double_damage_from"]:
                        pkmn_weaknesses.add(weak_to["name"])
            
            for w in pkmn_weaknesses:
                weaknesses_count[w] = weaknesses_count.get(w, 0) + 1
                
    # filter to show only shared weaknesses (2 or more pokemon weak to it)
    shared_weaknesses = {k: v for k, v in weaknesses_count.items() if v > 1}
    
    if shared_weaknesses:
        table = Table(title="critical team vulnerabilities", show_header=True)
        table.add_column("attack type", style="red bold")
        table.add_column("members weak to it", justify="center")
        
        sorted_w = sorted(shared_weaknesses.items(), key=lambda x: x[1], reverse=True)
        for w_type, count in sorted_w:
            table.add_row(w_type, str(count))
            
        console.print(table)
        console.print("[dim]note: showing types that are super effective against multiple members.[/dim]\n")
    else:
        console.print("[bold green]✓ good job! no shared weaknesses found across the team.[/bold green]\n")

if __name__ == "__main__":
    my_team = build_team()
    display_team(my_team)
    analyze_weaknesses(my_team)