Contributions welcome. You will need to set up virtualenv and adhere to autopep8 style (TBC, TODO). 
We use Travis-CI, so your code will be checked against autopep8, before it's tested or run. Please make all tests pass before sending a PR. 

## Workflow summary
Fork my repo, git clone your repo locally, checkout a new branch, commit changes, push up to your repo, run tests and open a PR.

## Step-by-step guide
Fork on GitHub
```bash
git clone https://github.com/<your_username>/solent.git
cd income_calc
git checkout -b new_feature_branch
```
hack, hack, hack

```bash
git commit -am "meaningful commit message"
git push origin new_feature_branch
```
Use the GitHub UI to send a PR, Travis-CI should start automatically.
