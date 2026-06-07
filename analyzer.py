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

def analyze_matchups(team):
    if not team:
        return
        
    console.print("\n[bold cyan]--- team matchup analysis ---[/bold cyan]")
    
    weak_count = {}
    resist_count = {}
    
    with console.status("analyzing type matchups...", spinner="dots"):
        for p in team:
            p_weak = set()
            p_resist = set()
            
            for t in p["types"]:
                type_data = get_type_data(t)
                if type_data:
                    # check weaknesses
                    for w in type_data["double_damage_from"]:
                        p_weak.add(w["name"])
                    
                    # check resistances and immunities
                    for r in type_data["half_damage_from"]:
                        p_resist.add(r["name"])
                    for i in type_data["no_damage_from"]:
                        p_resist.add(i["name"])
                        
            # basic cancellation logic (if weak and resistant -> neutral)
            for w in p_weak:
                if w not in p_resist:
                    weak_count[w] = weak_count.get(w, 0) + 1
                    
            for r in p_resist:
                if r not in p_weak:
                    resist_count[r] = resist_count.get(r, 0) + 1

    # display vulnerabilities table
    shared_weak = {k: v for k, v in weak_count.items() if v > 1}
    if shared_weak:
        t_weak = Table(title="critical vulnerabilities", show_header=True)
        t_weak.add_column("attack type", style="red bold")
        t_weak.add_column("members weak to it", justify="center")
        
        for w, c in sorted(shared_weak.items(), key=lambda x: x[1], reverse=True):
            t_weak.add_row(w, str(c))
        console.print(t_weak)
    else:
        console.print("[bold green]✓ no major shared vulnerabilities.[/bold green]")

    # display resistances table
    shared_resist = {k: v for k, v in resist_count.items() if v > 1}
    if shared_resist:
        t_resist = Table(title="solid team resistances", show_header=True)
        t_resist.add_column("attack type", style="green bold")
        t_resist.add_column("members resisting it", justify="center")
        
        for r, c in sorted(shared_resist.items(), key=lambda x: x[1], reverse=True):
            t_resist.add_row(r, str(c))
        console.print(t_resist)
        console.print("[dim]note: showing types that multiple members resist.[/dim]\n")

if __name__ == "__main__":
    my_team = build_team()
    display_team(my_team)
    analyze_matchups(my_team)