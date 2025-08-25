# Ozernik Discord Bot

Ozernik is a custom Discord bot developed exclusively for the [Озёрники](https://discord.com/invite/VjtB5CQ) server.

## Important Notice

This bot is specifically designed for the Озёрники server and may not function correctly on other servers.

## Features

- **Voice Channel Management**: Allows authorized users to rename voice channels.
- **Role Management**: Facilitates the transfer of duelist roles between members.

## Prerequisites

- Python 3.8 or higher
- All required Python packages are listed in `requirements.txt`.

## Installation and Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Berej/ozernik.git
   ```

2. **Navigate to the project directory**:

   ```bash
   cd ozernik
   ```

3. **Create a virtual environment**:

   ```bash
   python -m venv .venv
   ```

4. **Activate the virtual environment**:

   - On Windows:

     ```bash
     .venv\Scripts\activate
     ```

   - On Unix or MacOS:

     ```bash
     source .venv/bin/activate
     ```

5. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

   or

   ```bash
   python3 -m pip install -r requirements.txt
   ```

6. **Configure the bot**:

   - Create `token.txt` and place your bot token!
7. **Run the bot**:

   ```bash
   python bot.py
   ```

## License

This project is licensed under the GPL-3.0 License.
