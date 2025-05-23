![image](screenshot.jpeg)

### Development Preparation

1. Based on `.env.example`, create `src/.env`.
2. Based on `env.test.example`, create `.env.test`.
3. Create virtual environment:
    ```bash
    uv venv -p src/venv
    ```
4. Install dependencies:
    ```bash
    make install
    ```
5. Obtain `credentials.json`:
   Before running tests, you must obtain the ID Token. Run `make login` to authenticate in the browser and save the ID Token and Refresh Token into `credentials.json`.

---

### Common Commands

| Command      | Description                                                                                                     |
| ------------ | --------------------------------------------------------------------------------------------------------------- |
| make dev     | Start Firebase emulators. The local endpoint will be `http://127.0.0.1:5001/taiwan-geodoc-hub/us-central1/upload`. |
| make login   | Obtain ID Token and Refresh Token and save them into `credentials.json`.                                        |
| make format  | Format the code.                                                                                                |
| make lint    | Lint the code.                                                                                                  |
| make test    | Run tests.                                                                                                      |
| make deploy  | Deploy to Firebase Functions.                                                                                   |
| make tree    | List the project structure.                                                                                     |