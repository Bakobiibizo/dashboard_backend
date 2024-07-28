from ast import literal_eval
from data_models import comx, wallet


class ComxCommandManager:
    def __init__(self, querymap_path="./query_maps"):
        self.querymap_path = querymap_path
        self.query_maps = {}
        self.commands_list = []
        self.commands_string = ""
        self.commands = {}
        self.keypair = None
        self.wallet = wallet
        
    def get_command_list(self):
        commands = comx.__dir__()
        self.commands_list = [command for command in commands if not command.startswith("_")]
        return self.commands_list

    def get_commands_string(self):
        self.commands_string = "\n".join(self.commands_list)
        return self.commands_string
        
    def get_commands_dict(self):
        for command in self.commands_list:
            self.commands[command] = comx.__getattribute__(command)
        return self.commands

    def get_query_map_list(self):
        for command in self.commands_list:
            if command.startswith("query_map_"):
                self.query_maps[command] = comx.__getattribute__(command)
        return self.query_maps
                
    def _execute_command(self, command_name, **kwargs):
        self.validate_user()
        if command_name not in self.commands.keys():
            raise ValueError(f"Command {command_name} not found. Available commands: {self.commands_list}")
        else:
            return self.commands[command_name](**kwargs)
        
    def execute_query_map(self, query_map_name, **kwargs):
        if query_map_name not in self.query_maps:
            raise ValueError(f"Query map {querymap} not found")
        return self.query_maps[querymap](**kwargs)
        