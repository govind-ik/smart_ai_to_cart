steps to install

1.install python
2.install pipx
  a.python -m pip install --user pipx
  b.python -m pipx ensurepath
3.install uv
  a.pipx install uv
4.create virtual environment
  a.uv venv .venv
5.activate virtual env
  a..venv\Scripts\activate
6.install all dependentcies from requirements.txt
  a.uv pip install -r requirements.txt
  


