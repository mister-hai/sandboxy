
class CtfdAuth():
    '''
    This is an example I have taken from soemwhere ( i dont remember)
    I am going to entirely rewrite it using it as a "doing the thing" guide
    '''
    '''do I need this?'''
    def do_auth(self, args: argparse.Namespace):
        """ Authenticate and write a new .ctfd-auth file """

        url = args.url.rstrip("/")

        session = requests.Session()

        r = session.get(f"{url}/login", allow_redirects=False)
        if r.status_code == 302 and r.headers["Location"].endswith("/setup"):
            print(
                f"[red]error[/red]: this ctfd installation has not been setup yet (hint: run `install`)"
            )
            return

        # Grab the nonce
        nonce = r.text.split("csrfNonce': \"")[1].split('"')[0]

        username = input("CTFd Username: ")
        password = getpass.getpass("CTFd Password: ")

        r = session.post(
            f"{url}/login",
            data={
                "name": username,
                "password": password,
                "_submit": "Submit",
                "nonce": nonce,
            },
            allow_redirects=False,
        )
        if r.status_code != 302 or not r.headers["Location"].endswith("/challenges"):
            print("[red]error[/red]: invalid login credentials")
            return

        r = session.get(f"{args.url}/settings")
        nonce = r.text.split("csrfNonce': \"")[1].split('"')[0]

        r = session.post(
            f"{url}/api/v1/tokens", json={}, headers={"CSRF-Token": nonce}
        )
        if r.status_code != 200 or not r.json()["success"]:
            print("[red]error[/red]: token generation failed")
            return

        print("writing ctfd auth configuration")
        token = r.json()["data"]["value"]
        with open(".ctfd-auth", "w") as filp:
            yaml.dump({"url": args.url, "token": token}, filp)
