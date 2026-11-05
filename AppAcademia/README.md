# Academia Sport Fitness

Aplicativo desktop para cadastro e consulta de clientes e funcionários de uma academia. Foi desenvolvido em Python, usando Tkinter para a interface e SQLite para guardar os dados localmente.

## Requisitos

- Python 3 instalado no Windows.
- Tkinter, que normalmente já acompanha a instalação oficial do Python para Windows.

O programa usa apenas bibliotecas que acompanham o Python; não há um `requirements.txt` necessário neste momento.

## Como executar

1. Abra esta pasta no Visual Studio Code.
2. Abra o arquivo `app_academia.py`.
3. No terminal integrado do VS Code, confirme que está nesta pasta e execute:

   ```powershell
   python app_academia.py
   ```

O banco `academia_app.db` é criado automaticamente nesta mesma pasta quando o programa é executado pela primeira vez. Mantenha o arquivo Python e o banco no mesmo local ao usar o aplicativo.

## Pastas do projeto

Este projeto é um aplicativo desktop único. As pastas `web`, `back` e `mobile` do exemplo não se aplicam à versão atual: não existe uma interface web, uma API/backend separado nem um aplicativo móvel. Não crie essas pastas vazias; se o projeto ganhar essas versões no futuro, elas poderão ser adicionadas.

## Git e dados locais

O arquivo `.gitignore` exclui o banco de dados SQLite e arquivos temporários do Python. Não envie ao GitHub um banco real que contenha dados de clientes ou funcionários.

O código atual define um acesso inicial de administrador (`admin` / `admin123`). Essas credenciais estão no próprio código; prefira manter o repositório privado enquanto elas permanecerem assim. Não use esse acesso padrão em um sistema publicado ou com dados reais.
