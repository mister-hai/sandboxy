class Config(object):
    def edit(self):
        '''
        ctfcli config edit

            Edit config with $EDITOR
        '''
        editor = os.getenv("EDITOR", "vi")
        command = editor, get_config_path()
        subprocess.call(command)

    def path(self):
        '''
        ctfcli config path

            Show config path
        '''
        click.echo(get_config_path())

    def view(self, color=True, json=False):
        '''
        ctfcli config view

            view the config
        '''
        config = get_config_path()
        with open(config) as f:
            if json is True:
                config = preview_config(as_string=True)
                if color:
                    config = highlight(config, JsonLexer(), TerminalFormatter())
            else:
                config = f.read()
                if color:
                    config = highlight(config, IniLexer(), TerminalFormatter())

            print(config)
