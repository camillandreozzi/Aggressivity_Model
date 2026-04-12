# Interactive app patch

## Add these files to the repo

- `streamlit_app.py`
- `src/egt_core/`
- `.github/workflows/app-smoke-test.yml`

## Add dependency

Append this to `requirements.txt`:

```txt
streamlit
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment

Use Streamlit Community Cloud and point it to `streamlit_app.py`.
