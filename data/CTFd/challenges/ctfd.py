def change_state(self, challenge:str, state:str):
    '''
    toggle challenge from visible to hidden
            This is obviously after the main list has been generated
    '''
    visible = {}
    hidden = {}
    try:
            if state not in ['visible', 'hidden']:
                raise Exception
    except Exception:
            errorlogger("[-] INVALID INPUT: {} {}".format(challenge,state))

    categories = self.get_categories()
    # maybe this would be better with dicts?
    for category in categories:
        visible[category] = []
        hidden[category] = []

    for challenges in self.challengelistyaml:
        #filter empties
        if challenge in challenges:
            # get category of challenge
            for category in self.challengelistyaml[challenge]:
                # for each challenge in that category
                for challenge in self.challengelistyaml[challenge][category]:
                    # read the challenge.yml file into a buffer
                    challengeyaml = self.loadchallengeyaml(category,challenge)
                    # obtain state of the challenge
                    challengeyaml['state'] = state
                    # toggle to invisible
                    if state == 'visible':
                        name = challengeyaml['name'].lower().replace(' ', '-')
                        if 'expose' in challenge_yml:
                            visible[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                        else:
                            visible[category].append({'name': name, 'port': 0})
                    else:
                        if 'expose' in challenge_yml:
                            hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                        else:
                            hidden[category].append({'name': name, 'port': 0})
                    chall = self.readchallengeintobuffer(category,challenge)
                    yaml.dump(challengeyaml, chall, sort_keys=False)
        else:
            for category in self.challengelistyaml[wave]:
                for challenge in self.challengelistyaml[wave][category]:
                    chall = open(f'{category}/{challenge}/challenge.yml', 'r')
                    challenge_yml = yaml.load(chall, Loader=yaml.FullLoader)
                    challenge_yml['state'] = 'hidden'
                    name = challenge_yml['name'].lower().replace(' ', '-')
                    if 'expose' in challenge_yml:
                        hidden[category].append({'name': name, 'port': challenge_yml['expose'][0]['nodePort']})
                    else:
                        hidden[category].append({'name': name, 'port': 0})
    return visible, hidden

# Firewall rules for visible challenges
def firewall(visible, hidden):
    rules = os.popen('gcloud compute firewall-rules --format=json list').read()

    for category in visible:
        for challenge in visible[category]:
            if challenge['port'] and challenge['name'] not in rules:
                os.system(
                    f"""
                        gcloud compute firewall-rules create {challenge['name']} \
                            --allow tcp:{challenge['port']} \
                            --priority 1000 \
                            --target-tags challs
                    """
                )
                print('Created firewall rules for:')
                print(challenge['name'])
    
    for category in hidden:
        for challenge in hidden[category]:
            if challenge['port'] and challenge['name'] in rules:
                os.system(
                    f"""
                        echo -e "Y\n" | gcloud compute firewall-rules delete {challenge['name']}
                    """
                )
                print('Deleted firewall rules for:')
                print(challenge['name'])    


# Synchronize each category in it's own thread.
if __name__ == "__main__":
    visible, hidden = change_state(['wave1', 'wave2'], 'visible')

    init()
    categories = get_categories()

    jobs = []
    for category in categories:
        jobs.append(threading.Thread(target=sync, args=(category, )))
    
    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    print("Synchronized successfully!")
    print("The following challenges are now visible:")

    for category in visible:
        print(f"\n{category}:")
        print('- ' + '\n- '.join([challenge['name'] for challenge in visible[category]]))

    firewall(visible, hidden)
    print("Firewall rules updated.")
