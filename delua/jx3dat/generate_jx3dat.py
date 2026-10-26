def generate_casting_items(start_id, end_id):
    items = []
    for dwid in range(start_id, end_id + 1):
        item = f"""{{
    dwID = {dwid},
}}"""
        items.append(item)
    return items

def generate_jx3dat(start_id, end_id):
    casting_items = generate_casting_items(start_id, end_id)
    casting_content = ",\n".join(casting_items)
    
    template = f"""return {{
	BUFF = {{}},
	DEBUFF = {{
    }},
	CHAT = {{}},
	CASTING = {{
	}},
	TALK = {{}},
	NPC = {{
    	[-1] = {{{casting_content},}},

    }},
	DOODAD = {{}},
}}"""
    
    return template

def main():
    print("JX3 CASTING Data Generator")
    print("-" * 40)
    
    try:
        start_id = int(input("Enter start dwID (a): "))
        end_id = int(input("Enter end dwID (b): "))
        
        if start_id > end_id:
            print("Error: start > end!")
            return
        
        print(f"Generating {start_id} to {end_id}...")
        content = generate_jx3dat(start_id, end_id)
        
        with open("new.jx3dat", 'w', encoding='utf-8') as f:
            f.write(content)
        
        count = end_id - start_id + 1
        print(f"Done! {count} entries created in new.jx3dat")
        
    except ValueError:
        print("Error: Invalid input!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
