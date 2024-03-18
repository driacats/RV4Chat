#! /bin/python
# Author: Andrea Gatti

import questionary, os, sys, subprocess, time

def interactive_setup():
    questionary.print('You can choose between 2 different domains:', style='italic')
    questionary.print(' (1) ', end='')
    questionary.print('Domestic Violence Domain', style='bold')
    questionary.print('     A chatbot that helps the user with domestic violence problems.', style='italic')
    questionary.print(' (2) ', end='')
    questionary.print('Factory Domain', style='bold')
    questionary.print('     A chatbot that helps the user to place robots inside a virtual factory.', style='italic')

    domain = questionary.select(
        'What domain do you want to try?',
        choices=['Domestic Violence', 'Factory'],
    ).ask()

    questionary.print('You can launch the example either with a Rasa or a Dialogflow backend.', style='italic')
    platform = questionary.select(
        'What backend do you want to use?',
        choices=['Dialogflow', 'Rasa'],
    ).ask()

    questionary.print('There are 3 different monitoring levels you can try:', style='italic')
    questionary.print(' (1) ', end='')
    questionary.print('No Monitor', style='bold')
    questionary.print('     Simply try the chatbot without the monitor;', style='italic')
    questionary.print(' (2) ', end='')
    questionary.print('Dummy Monitor', style='bold')
    questionary.print('     A monitor that returns always True;', style='italic')
    questionary.print(' (3) ', end='')
    questionary.print('Real Monitor', style='bold')
    questionary.print('     The monitor that checks properties.', style='italic')

    monitor = questionary.select(
        'What monitoring level do you want to use?',
        choices=['No Monitor', 'Dummy Monitor', 'Real Monitor'],
    ).ask()

    prop = None
    if (monitor == 'Real Monitor'):
        questionary.print('You can choosen between different properties for this domain.')
        p_folder = f'./{domain}/Monitor/Properties'
        properties = [f for f in os.listdir(p_folder) if f.endswith('.rml')]
        properties.append('Choose a custom one.')
        prop = questionary.select(
            'What property do you want to use?',
            choices=properties,
        ).ask()

        if (prop == 'Choose a custom one.'):
            prop = questionary.path('Path to the custom rml property to use').ask()

    questionary.print('\n󱓥 SUMMARY 󱓥 ', style='bold')
    questionary.print(f'- Domain: {domain}')
    questionary.print(f'- Backend: {platform}')
    questionary.print(f'- Monitor: {monitor}')
    if (monitor == 'Real Monitor'):
        questionary.print(f'- Property: {p}')

    if not (questionary.confirm('Do you confirm your choices?').ask()):
        print('Exiting.')
        return None
    return domain, platform, monitor, prop

def interactive_run(domain, platform, monitor, prop):
    print(domain)
    test_monitor = {'No Monitor': 'no-monitor', 'Dummy Monitor': 'dummy-monitor', 'Real Monitor': 'real-monitor'}
    service = subprocess.Popen(f'kitty --hold 2>/dev/null sh -c \'cd "{domain}" && python start_service.py -s -p {platform.lower()} -m {test_monitor[monitor]}\'', shell=True, preexec_fn=os.setsid)
    time.sleep(2)
    os.system('python chat.py')
## TEST RUN

def test_run(test):
    for domain in test:
        for platform in test[domain]:
            for monitor in test[domain][platform]['monitors']:
                test_monitor = {'No Monitor': 'no-monitor', 'Dummy Monitor': 'dummy-monitor', 'Real Monitor': 'real-monitor'}
                # test_py.launch_tests([platform], [monitor])
                os.system(f'cd "{domain}" && python run_test.py -p {platform} -m {test_monitor[monitor]}')


def test_ask_platform(domain):
    questionary.print('In the examples are provided implementations both with Rasa and Dialogflow.', style='italic')
    platforms = questionary.checkbox(
        f'Which backend(s) do you want to test in the {domain} domain?',
        choices=['Dialogflow', 'Rasa'],
    ).ask()
    return platforms

def test_ask_monitors(domain, platform):
    questionary.print('There are 3 different monitoring levels you can test:', style='italic')
    questionary.print(' (1) ', end='')
    questionary.print('No Monitor', style='bold')
    questionary.print('     Simply try the chatbot without the monitor;', style='italic')
    questionary.print(' (2) ', end='')
    questionary.print('Dummy Monitor', style='bold')
    questionary.print('     A monitor that returns always True;', style='italic')
    questionary.print(' (3) ', end='')
    questionary.print('Real Monitor', style='bold')
    questionary.print('     The monitor that checks properties.', style='italic')

    monitors = questionary.checkbox(
        f'With which monitor(s) do you want to launch the tests for {platform} in the {domain} domain?',
        choices=['No Monitor', 'Dummy Monitor', 'Real Monitor'],
    ).ask()

    prop = None

    if ('Real Monitor' in monitors):
        questionary.print('You can choosen between different properties for this domain.')
        p_folder = f'./{domain}/Monitor/Properties'
        ps = [f for f in os.listdir(p_folder) if f.endswith('.rml')]
        ps.append('Choose a custom one.')
        prop = questionary.select(
            f'What property do you want to use for {platform}?',
            choices=ps,
        ).ask()

        if (prop == 'Choose a custom one.'):
            prop = questionary.path('Path to the custom rml property to use').ask()

    return monitors, prop


def test_setup():
    questionary.print('In the examples are provided 2 different domains:', style='italic')
    questionary.print(' (1) ', end='')
    questionary.print('Domestic Violence Domain', style='bold')
    questionary.print('     A chatbot that helps the user with domestic violence problems.', style='italic')
    questionary.print(' (2) ', end='')
    questionary.print('Factory Domain', style='bold')
    questionary.print('     A chatbot that helps the user to place robots inside a virtual factory.', style='italic')
    
    domains = questionary.checkbox('On which domain(s) do you want to run the tests?', choices=['Domestic Violence', 'Factory']).ask()

    test = {}

    for domain in domains:
        platforms = test_ask_platform(domain)
        platform_json = {}
        for platform in platforms:
            monitors, prop = test_ask_monitors(domain, platform)
            p_json = {}
            p_json['monitors'] = monitors
            p_json['property'] = prop

            platform_json[platform] = p_json
        test[domain] = platform_json

    questionary.print('\n󱓥 SUMMARY 󱓥 ', style='bold')
    for domain in test:
        questionary.print(f'{domain.upper()}', style='bold')
        for platform in test[domain]:
            questionary.print(f'Platform: {platform}')
            questionary.print(f'  Monitors:')
            for monitor in test[domain][platform]['monitors']:
                questionary.print(f'    {monitor}')
            questionary.print(f'  Property: {test[domain][platform]["property"]}')

    if (questionary.confirm('Do you confirm your choice?').ask()):
        test_run(test)

def main():
    questionary.print('  RV4CHAT EXAMPLES  ', style='bold')
    questionary.print('This script helps you running the examples.', style='italic')
    mode = questionary.select(
        'Do you want to launch the tests or try interactively the chat?',
        choices = ['Run the tests', 'Try the chat']
    ).ask()
    if (mode == 'Try the chat'):
        domain, platform, monitor, prop = interactive_setup()
        interactive_run(domain, platform, monitor, prop)
    elif (mode == 'Run the tests'):
        test_setup()
    else:
        print('Error, exiting.')

if (__name__ == '__main__'):
    main()