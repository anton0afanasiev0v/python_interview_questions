data = { 
    "srv1": { 
        "cpu": "70%", 
        "owner": "max_katz" 
    }, 
    "srv2": { 
        "cpu": "12%", 
        "owner": "dmitry_3" 
    }, 
    "srv3": { 
        "cpu": "43%", 
        "owner": "max_katz" 
    } 
}


def convert(): 
    result = {}
    for server_name, server_data in data.items():
        owner = server_data["owner"]
        cpu_value = server_data["cpu"]
        server_entry = {server_name: {"cpu": cpu_value}}
        if owner not in result:
            result[owner] = []
        result[owner].append(server_entry)
    print(result)
    return result


assert { 
    'max_katz': [ 
        {'srv1': { 
            'cpu': '70%'} 
        }, 
        {'srv3': { 
            'cpu': '43%'}          
        } 
    ], 
    'dmitry_3': [ 
        {'srv2': { 
            'cpu': '12%'}        
        } 
    ] 
} == convert()