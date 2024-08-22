import os
import sys
from github import Github, GithubException
from dotenv import load_dotenv
import click


load_dotenv()



def dict_select(d, prompt, allow_None=False):
    click.echo(prompt)
    click.echo("\n".join([f"{i}: {name}" for i,name in enumerate(d.keys())]))


    while True:
        try:
            choice = int(input("")) if allow_None else int(click.prompt("", type=click.INT))
        except ValueError:
            return (None, None)
        if choice in list(range(len(d.keys()))):
            break
        if allow_None:
            return (None, None)
        click.echo("Invalid option")

    return (list(d.keys())[choice], d[list(d.keys())[choice]])






# establish the git account ot use to perform this action
TOKENS = [x.strip() for x in os.getenv("GITHUB_TOKENS").split(",") if not x.strip()==""]

if len(TOKENS) == 0:
    click.echo("No GitHub tokens found in .env file please add personal access tokens to GITHUB_TOKENS: https://github.com/settings/personal-access-tokens/new")
    exit()

ACCOUNTS = dict()
ACCOUNT = None


INIT_REPO = """
cd {HOME_DIR}
git clone {clone_url}
cd {name}

git config user.name "{user_name}"
git config user.email {user_email}

"""


PUSH_REPO = """
cd {HOME_DIR}
git clone {clone_url}
cd {name}

git add -A
git commit -m "Initial commit"

git push -u origin main
"""


@click.group()
def cli():
    pass

@click.command()
@click.argument('name', type=str)
@click.option('--private', is_flag=True, help="Make the repository private")
def make(name, private):
    """Creates a new repository on GitHub and clones it"""

    for i in TOKENS:
        g = Github(i)

        ACCOUNTS[g.get_user().login] = g

    if len(ACCOUNTS.keys()) > 1:
        username, ACCOUNT = dict_select(ACCOUNTS, "Select a GitHub account to use:")
        
    else:
        ACCOUNT = ACCOUNTS[list(ACCOUNTS.keys())[0]]

    click.echo(f"Using GitHub account: {ACCOUNT.get_user().login}")

    name = name.lower().replace(" ", "_").replace("-", "_")

    user = ACCOUNT.get_user()

    while True:
        if click.confirm("Confirm {} repository creation".format("Private" if private else "Public"), default=True): break
        private = not private

    try:
        repo = user.create_repo(name, private=private)
    except GithubException:
        repo = user.get_repo(name)

    email = [x.email for x in user.get_emails() if x.email.endswith("@users.noreply.github.com")][0]


    # Clone the repository into $HOME_DIR
    create_code = INIT_REPO.format(name=name, clone_url=repo.clone_url, HOME_DIR=os.getenv("HOME_DIR"), user_name=user.name, user_email=email)

    os.system(create_code )

    # Create initial files

    repo_dir = os.path.join(os.getenv("HOME_DIR"), name)

    os.system("touch {}/README.md".format(repo_dir))

    with open("{}/README.md".format(repo_dir), "w") as f:
        f.write(f"# {name}\n\nThis is a new repository created by {user.name} using https://github.com/muntedcrocodile/makenewproject")

    os.system("touch {}/.gitignore".format(repo_dir))

    selected_ignores = list()

    while True:
        search = click.prompt("Search git ignore templates")

        ignore_files = [x for x in os.listdir("./gitignore") if x.endswith(".gitignore")]
        searched_files = [x for x in ignore_files if search.lower() in x.lower()]

        selected_ignore, _ = dict_select({".".join(x.split(".")[:-1:]):x for x in searched_files}, "Select a gitignore template to use:", allow_None=True)
        if selected_ignore is None:
            click.echo("Selected ignores: "+str(selected_ignores))
            if click.confirm("Finished?"): break
            continue

        selected_ignores.append(selected_ignore)
        click.echo("Selected ignores: "+str(selected_ignores))
        if click.confirm("Finished?"): break

    # write the selected gitignore templates to the .gitignore file
    with open("{}/.gitignore".format(repo_dir), "w") as f:
        for i in selected_ignores:
            with open(f"./gitignore/{i}.gitignore", "r") as g:
                f.write(g.read())


    os.system("touch {}/LICENSE".format(repo_dir))

    selected_licence = None

    while True:
        search = click.prompt("Search licenses")

        licence_files = os.listdir("./license-templates/templates/")
        searched_files = [x for x in licence_files if search.lower() in x.lower()]

        selected_licence, _ = dict_select({".".join(x.split(".")[:-1:]):x for x in searched_files}, "Select a licence template to use:", allow_None=True)

        click.echo("Selected Licence: "+str(selected_licence))
        if click.confirm("Finished?"): break

    # write the selected licence template to the LICENSE file
    with open("{}/LICENSE".format(repo_dir), "w") as f:
        with open(f"./license-templates/templates/{selected_licence}.txt", "r") as g:
            f.write(g.read())

    os.system("codium {} {}/README.md".format(repo_dir, repo_dir))


    if click.confirm("Push to GitHub?", default=True):
        push_code = PUSH_REPO.format(name=name, clone_url=repo.clone_url, HOME_DIR=os.getenv("HOME_DIR"), user_name=user.name, user_email=email)
        os.system(push_code)





cli.add_command(make)

if __name__ == '__main__':
    try:
        cli()
    except (KeyboardInterrupt, SystemExit, click.exceptions.Abort):
        pass