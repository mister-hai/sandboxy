# Firewall rules for visible challenges
# with google cloud
    def firewall(visible, hidden):
        """
        NOT IMPLEMENTED YET

        turn visible into ON
        turn hidden into OFF
        
        FIRST PARAM shall be state to set firewall to
        SECOND PARAM shall be the challenge to generate a firewall rule for
        """
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