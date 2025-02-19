from datetime import datetime
import json
import time
from colorama import Fore
import requests
import itertools

class hashcat:
    BASE_URL = "https://hashcats-gateway-ffa6af9b026a.herokuapp.com/"
    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "connection": "keep-alive",
        "host": "hashcats-gateway-ffa6af9b026a.herokuapp.com",
        "origin": "https://hashcatsapp.com",
        "referer": "https://hashcatsapp.com/",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    def __init__(self):
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.coins = 0

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 HashCat Free Bot", Fore.CYAN)
        self.log("🚀 Created by LIVEXORDS", Fore.CYAN)
        self.log("📢 Channel: t.me/livexordsscript\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
            print(Fore.LIGHTBLACK_EX + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |") + " " + color + message + Fore.RESET)

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log("❌ Failed to parse config.json. Please check the file format.", Fore.RED)
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔒 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        req_url = f"{self.BASE_URL}users"
        token = self.query_list[index]

        self.log(
            f"📋 Using token: {token[:10]}... (truncated for security)",
            Fore.CYAN,
        )

        headers = {**self.HEADERS, "authorization": f"tma {token}"}

        try:
            self.log(
                "📡 Sending request to fetch user information...",
                Fore.CYAN,
            )
            
            response = requests.get(req_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            auth_token = response.headers.get("authorization", None)
            if auth_token:
                self.token = auth_token
                self.log("🔑 Authorization token successfully retrieved.", Fore.GREEN)
            else:
                self.log("⚠️ Authorization token not found in response headers.", Fore.YELLOW)

            if "user" in data:
                user_info = data["user"]
                username = user_info.get("userName", "Unknown")
                coin = data.get("minedCoins", 0)
                promo_code = user_info.get("promoCode", "N/A")
                own_promo_code = user_info.get("ownPromoCode", "N/A")
                shard = user_info.get("shard", "Unknown")
                last_login = user_info.get("lastLogin", "Unknown")
                
                self.log("✅ Login successful!", Fore.GREEN)
                self.log(f"👤 Username: {username}", Fore.LIGHTGREEN_EX)
                self.log(f"💎 Coin: {coin}", Fore.CYAN)
                self.log(f"🏷️ Promo Code: {promo_code}", Fore.LIGHTYELLOW_EX)
                self.log(f"🏷️ Own Promo Code: {own_promo_code}", Fore.LIGHTYELLOW_EX)
                self.log(f"🔢 Shard: {shard}", Fore.LIGHTBLUE_EX)
                self.log(f"⏰ Last Login: {last_login}", Fore.LIGHTMAGENTA_EX)
            else:
                self.log(
                    "⚠️ Unexpected response structure.", Fore.YELLOW
                )

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send login request: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)

    def update_balance(self) -> int:
        """Updates the user's balance from the server."""
        req_url_balance = f"{self.BASE_URL}users/balance"
        headers = {**self.HEADERS, "authorization": self.token}

        try:
            self.log("📡 Fetching updated balance...", Fore.CYAN)
            response = requests.get(req_url_balance, headers=headers)
            response.raise_for_status()

            balance_data = response.json()
            if "balance" not in balance_data:
                raise ValueError("Balance data is missing in the response.")

            updated_balance = int(balance_data["balance"])  # Ensure balance is an integer
            self.log(f"✅ Balance updated successfully: {updated_balance}", Fore.GREEN)

            return updated_balance

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch balance: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0  # Return 0 if updating the balance fails
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
            self.log(f"📄 Response content: {response.text}", Fore.RED)
            return 0
    
    def daily(self) -> None:
        req_url_daily = f"{self.BASE_URL}users/claim-daily-task"
        headers = {**self.HEADERS, "authorization": self.token}

        try:
            self.log("✨ Starting daily reward claim process...", Fore.CYAN)

            response = requests.post(req_url_daily, headers=headers, json={})

            if response.status_code == 400:
                self.log("❌ Daily reward has already been claimed! ⏳ Try again tomorrow.", Fore.YELLOW)
                self.log(f"📄 Response Content: {response.text}", Fore.CYAN)
                return
            elif response.status_code != 200:
                self.log(f"⚠️ Failed to claim daily reward. Status Code: {response.status_code}", Fore.RED)
                self.log(f"📄 Response Content: {response.text}", Fore.CYAN)
                return

            daily_data = response.json()
            strike = daily_data.get("strike", 0)
            last_claimed = daily_data.get("lastClaimed", "Unknown")
            balance = daily_data.get("balance", "0")
            stacked_balance = daily_data.get("stackedBalance", "0")

            self.log(
                "🎉 Daily Reward Claimed Successfully!",
                Fore.GREEN
            )
            self.log(f"🔥 Strike Count: {strike}", Fore.YELLOW)
            self.log(f"⏳ Last Claimed: {last_claimed}", Fore.YELLOW)
            self.log(f"💰 Current Balance: {balance}", Fore.YELLOW)
            self.log(f"📦 Stacked Balance: {stacked_balance}", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error while claiming daily reward: {e}", Fore.RED)
            self.log(f"📄 Response Content: {response.text}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error: Unable to process reward details: {e}", Fore.RED)
            self.log(f"📄 Response Content: {response.text}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error occurred: {e}", Fore.RED)
            self.log(f"📄 Response Content: {response.text}", Fore.RED)

    def card(self) -> None:
        """
        Manages card purchasing and upgrades, considering both profitability and purchase requirements.
        """
        req_url_cards = f"{self.BASE_URL}inventory/user/cards"
        req_url_equipment = f"{self.BASE_URL}inventory/cards"
        req_url_buy_card = f"{self.BASE_URL}users/buy-card"
        headers = {**self.HEADERS, "authorization": self.token}

        try:
            while True:
                user_coins = self.update_balance()
                if user_coins == 0:
                    self.log("❌ Balance is zero. Exiting card purchasing process.", Fore.RED)
                    break

                self.log(f"💰 Current balance: {user_coins}", Fore.YELLOW)

                self.log("📋 Fetching user card information...", Fore.CYAN)
                response = requests.get(req_url_cards, headers=headers)
                response.raise_for_status()
                user_cards_data = response.json()

                if not isinstance(user_cards_data, list):
                    raise ValueError("❌ Invalid response structure: user_cards_data is not a list.")

                user_cards = {card["cardId"]: card for card in user_cards_data}
                self.log("✅ Successfully fetched user card information.", Fore.GREEN)

                self.log("🛒 Fetching available cards to purchase...", Fore.CYAN)
                response = requests.get(req_url_equipment, headers=headers)
                response.raise_for_status()
                equipment_data = response.json().get("equipment", [])

                if not equipment_data:
                    self.log("❌ No cards available for purchase.", Fore.RED)
                    break

                # Find the best card
                best_card = None
                best_profit_increase = 0

                for card in equipment_data:
                    if not card.get("unlocked", False):
                        continue

                    card_id = card["id"]
                    user_card = user_cards.get(card_id)
                    current_level = user_card["level"] if user_card else 0

                    # Check if card requires another card at a specific level
                    requirements = card.get("requirementsJson")
                    if requirements:
                        required_card_id = requirements.get("requiredCardId")
                        required_card_level = requirements.get("requiredCardLevel")

                        if required_card_id:
                            required_card = user_cards.get(required_card_id)
                            if not required_card or required_card["level"] < required_card_level:
                                self.log(
                                    f"⚠️ Cannot purchase '{card['name']}' because it requires card ID {required_card_id} at level {required_card_level}.",
                                    Fore.YELLOW
                                )
                                continue

                    if current_level + 1 < len(card["profits"]):
                        next_level = current_level + 1
                        next_price = int(card["prices"][next_level])
                        profit_increase = int(card["profits"][next_level]) - int(card["profits"][current_level])

                        if next_price <= user_coins and profit_increase > best_profit_increase:
                            best_profit_increase = profit_increase
                            best_card = {
                                "id": card_id,
                                "name": card["name"],
                                "category": card["category"],
                                "next_level": next_level,
                                "next_price": next_price,
                                "profit_increase": profit_increase
                            }

                if best_card:
                    self.log(
                        f"🔝 Best card for upgrade: {best_card['name']} "
                        f"(Next Level: {best_card['next_level']}, Price: {best_card['next_price']}, Profit Increase: {best_card['profit_increase']})",
                        Fore.GREEN
                    )

                    payload = {"card_id": best_card["id"], "category": best_card["category"]}
                    self.log(f"🛒 Attempting to purchase upgraded card: {best_card['name']}...", Fore.CYAN)
                    buy_response = requests.post(req_url_buy_card, headers=headers, json=payload)

                    if buy_response.status_code == 403:
                        self.log(f"❌ Not enough balance to purchase '{best_card['name']}'.", Fore.RED)
                    elif buy_response.status_code != 200:
                        self.log(f"❌ Failed to purchase '{best_card['name']}'. Error code: {buy_response.status_code}", Fore.RED)
                        self.log(f"📄 Response Content: {buy_response.text}", Fore.RED)
                    else:
                        buy_data = buy_response.json()
                        user_coins = int(buy_data.get("balance", user_coins))
                        self.log(f"✅ '{best_card['name']}' card purchased successfully! New balance: {user_coins}", Fore.GREEN)
                else:
                    self.log("⚠️ No profitable cards available or requirements not met. Exiting.", Fore.YELLOW)
                    break

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch data from the server: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}", Fore.RED)
 
    def tap(self) -> None:
        req_url_start_tapping = f"{self.BASE_URL}users/start-tapping"
        req_url_save_tap_balance = f"{self.BASE_URL}users/save-tap-balance"
        headers = {**self.HEADERS, "authorization": self.token}
        payload_save_tap = {
            "tapBalance": 9000000
        }

        try:
            self.log("🟢 Starting tap process...", Fore.CYAN)

            # Step 1: Calculate current time in milliseconds
            current_time_ms = int(time.time() * 1000)
            payload_start_tapping = {"dateStartMs": current_time_ms}
            self.log(f"⏱ Current timestamp: {current_time_ms}", Fore.CYAN)

            # Step 2: Fetch tap token
            self.log("🚀 Fetching tap token...", Fore.CYAN)
            response_start = requests.post(req_url_start_tapping, headers=headers, json=payload_start_tapping)

            if response_start.status_code != 200:
                self.log(f"⚠️ Failed to start tapping. Status Code: {response_start.status_code}", Fore.RED)
                self.log(f"🔍 Response Content: {response_start.text}", Fore.CYAN)
                return

            start_data = response_start.json()
            tap_token = start_data.get("token")

            if not tap_token:
                self.log("❌ Error: Tap token not found in response!", Fore.RED)
                return

            self.log(f"🔑 Tap token fetched successfully: {tap_token}", Fore.GREEN)

            # Step 3: Save tap balance
            self.log("💾 Saving tap balance with 9,000,000...", Fore.CYAN)
            payload_save_tap["token"] = tap_token
            response_save = requests.post(req_url_save_tap_balance, headers=headers, json=payload_save_tap)

            if response_save.status_code != 200:
                self.log(f"⚠️ Failed to save tap balance. Status Code: {response_save.status_code}", Fore.RED)
                self.log(f"🔍 Response Content: {response_save.text}", Fore.CYAN)
                return

            save_data = response_save.json()
            energy = save_data.get("energy", 0)

            # Log the results
            self.log("🎉 Tap balance saved successfully!", Fore.GREEN)
            self.log(f"💰 New Balance: {save_data.get('balance', 'N/A')}", Fore.YELLOW)
            self.log(f"📦 Stacked Balance: {save_data.get('stackedBalance', 'N/A')}", Fore.YELLOW)
            self.log(f"⚡ Remaining Energy: {energy}", Fore.YELLOW)

            if energy == 0:
                self.log("⚠️ Energy depleted. Please recharge!", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error: {e}\nResponse: {e.response.text if e.response else 'No response'}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error: Unable to process response: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error occurred: {e}", Fore.RED)

    def farm(self):
        headers = {**self.HEADERS, "authorization": self.token}
        self.log("➡️ Starting farming process...", color=Fore.YELLOW)

        try:
            # Fetch farm slots
            self.log("📋 Fetching farm slots...", color=Fore.YELLOW)
            slots_response = requests.get(f"{self.BASE_URL}farm/slots", headers=headers)
            slots_response.raise_for_status()
            slots = slots_response.json()

            for slot in slots:
                try:
                    slot_id = slot["id"]
                    slot_title = slot.get("title", "Unknown Slot")
                    self.log(f"📂 Processing slot {slot_id} ({slot_title})...", color=Fore.CYAN)

                    # Determine currency type for the slot
                    currency = slot["price"]["currency"]
                    balance_key = "stackedBalance" if currency.startswith("red") else "balance"
                    self.log(f"🔍 Slot uses {currency} ({balance_key}).", color=Fore.GREEN)

                    farming = slot.get("farming")
                    if farming:
                        if farming.get("isFinished"):
                            farming_id = farming["id"]
                            self.log(f"🏆 Collecting rewards for slot {slot_id} ({slot_title}) and farming {farming_id}...", color=Fore.CYAN)
                            collect_response = requests.post(
                                f"{self.BASE_URL}farm/slot/{slot_id}/farming/{farming_id}/collect", 
                                headers=headers, 
                                json={}
                            )
                            if collect_response.status_code == 403:
                                self.log(f"❌ Forbidden while collecting rewards in slot {slot_id}. Skipping...", color=Fore.RED)
                                continue
                            collect_response.raise_for_status()
                            self.log(f"✅ Successfully collected rewards for slot {slot_id}.", color=Fore.GREEN)

                    # Fetch balance
                    self.log(f"💰 Fetching {balance_key} balance...", color=Fore.YELLOW)
                    balance_response = requests.get(f"{self.BASE_URL}users/balance", headers=headers)
                    balance_response.raise_for_status()
                    balance_data = balance_response.json()
                    balance = balance_data.get(balance_key, 0)
                    self.log(f"💳 Current {balance_key}: {balance} {currency}.", color=Fore.GREEN)

                    # Check for slot upgrade
                    next_price = slot["price"]["amount"]
                    if balance >= next_price:
                        self.log(f"⬆️ Upgrading slot {slot_id} ({slot_title}) with {next_price} {currency}...", color=Fore.GREEN)
                        upgrade_response = requests.post(
                            f"{self.BASE_URL}farm/slot/{slot_id}",
                            headers=headers,
                            json={}
                        )
                        if upgrade_response.status_code == 403:
                            self.log(f"❌ Forbidden while upgrading slot {slot_id}. Skipping...", color=Fore.RED)
                            continue
                        upgrade_response.raise_for_status()
                        self.log(f"✅ Successfully upgraded slot {slot_id}.", color=Fore.GREEN)

                    # Fetch components and attempt upgrades
                    self.log(f"⚙️ Fetching components for slot {slot_id}...", color=Fore.YELLOW)
                    components_response = requests.get(f"{self.BASE_URL}farm/slot/{slot_id}/components", headers=headers)
                    if components_response.status_code == 403:
                        self.log(f"❌ Forbidden while fetching components for slot {slot_id}. Skipping...", color=Fore.RED)
                        continue
                    components_response.raise_for_status()
                    components = components_response.json()

                    for component in components:
                        component_id = component["id"]
                        component_price = component["price"]["amount"]
                        if balance >= component_price:
                            self.log(f"🔧 Upgrading component {component_id} for slot {slot_id}...", color=Fore.CYAN)
                            component_upgrade_response = requests.post(
                                f"{self.BASE_URL}farm/component/{component_id}", 
                                headers=headers, 
                                json={}
                            )
                            if component_upgrade_response.status_code == 403:
                                self.log(f"❌ Forbidden while upgrading component {component_id}. Skipping...", color=Fore.RED)
                                continue
                            component_upgrade_response.raise_for_status()
                            self.log(f"✅ Successfully upgraded component {component_id}.", color=Fore.GREEN)

                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Network error in slot {slot_id}: {e}\nResponse: {e.response.text if e.response else 'No response'}", color=Fore.RED)
                except ValueError as e:
                    self.log(f"❌ Data error in slot {slot_id}: Unable to process response: {e}", color=Fore.RED)
                except Exception as e:
                    self.log(f"❌ Unexpected error in slot {slot_id}: {e}", color=Fore.RED)

            # Fetch boosters and attempt to buy free ones
            self.log("🎁 Fetching available boosters...", color=Fore.YELLOW)
            boosters_response = requests.get(f"{self.BASE_URL}farm/boosters", headers=headers)
            boosters_response.raise_for_status()
            boosters = boosters_response.json()

            for booster in boosters:
                if booster["id"] == 1 and booster["isPurchaseAvailable"]:
                    self.log(f"🎉 Buying free booster {booster['id']}...", color=Fore.CYAN)
                    booster_purchase_response = requests.post(
                        f"{self.BASE_URL}farm/boosters/{booster['id']}/buy", 
                        headers=headers, 
                        json={}
                    )
                    booster_purchase_response.raise_for_status()
                    self.log(f"✅ Successfully bought free booster {booster['id']}.", color=Fore.GREEN)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error during farming process: {e}\nResponse: {e.response.text if e.response else 'No response'}", color=Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error during farming process: Unable to process response: {e}", color=Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error occurred during farming process: {e}", color=Fore.RED)

    def stack_balance(self):
        headers = {**self.HEADERS, "authorization": self.token}
        self.log("🔄 Starting stacking process...", color=Fore.YELLOW)

        try:
            # Fetch current balance
            self.log("💰 Fetching current balance...", color=Fore.YELLOW)
            balance_response = requests.get(f"{self.BASE_URL}users/balance", headers=headers)
            balance_response.raise_for_status()
            balance_data = balance_response.json()

            balance = balance_data.get("balance", 0)
            self.log(f"💳 Current balance: {balance}", color=Fore.GREEN)

            if balance > 0:
                # Fetch cat details
                self.log("🐱 Fetching cat details...", color=Fore.YELLOW)
                cat_response = requests.get(f"{self.BASE_URL}users/cat", headers=headers)
                cat_response.raise_for_status()
                cat_data = cat_response.json()

                # Extract APY from cat details
                apy = cat_data.get("apy", 0)
                self.log(f"📈 APY from cat: {apy}", color=Fore.GREEN)

                # Calculate staking amount
                staking_amount = balance * (apy / 100)
                self.log(f"⬆️ Calculated staking amount: {staking_amount}", color=Fore.CYAN)

                # Perform staking
                payload = {"amount": staking_amount}
                self.log(f"⬆️ Stacking balance with amount: {staking_amount}...", color=Fore.CYAN)
                stack_response = requests.post(f"{self.BASE_URL}users/stack-balance", headers=headers, json=payload)
                stack_response.raise_for_status()

                self.log("✅ Successfully stacked balance.", color=Fore.GREEN)
            else:
                self.log("⚠️ Balance is zero. Nothing to stack.", color=Fore.YELLOW)

        except requests.exceptions.HTTPError as http_err:
            self.log(f"❌ HTTP error occurred: {http_err}", color=Fore.RED)
            if http_err.response:
                self.log(f"🔍 Server response: {http_err.response.text}", color=Fore.RED)

        except requests.exceptions.RequestException as req_err:
            self.log(f"❌ Network error during stacking process: {req_err}", color=Fore.RED)
            if req_err.response:
                self.log(f"🔍 Server response: {req_err.response.text}", color=Fore.RED)

        except ValueError as e:
            self.log(f"❌ Data error: Unable to process response: {e}", color=Fore.RED)

        except Exception as e:
            self.log(f"❌ Unexpected error occurred during stacking process: {e}", color=Fore.RED)

    def reff(self) -> None:
        req_url_reff = f"{self.BASE_URL}users/claim-refs-mining"
        headers = {**self.HEADERS, "authorization": self.token}

        try:
            self.log("✨ Starting claim referral benefit process...", Fore.CYAN)

            response = requests.get(req_url_reff, headers=headers)

            self.log(f"📄 Full Response Content: {response.text}", Fore.CYAN)

            if response.status_code != 200:
                self.log(f"⚠️ Failed to claim referral benefit. Status Code: {response.status_code}", Fore.RED)
                return

            reff_data = response.json()

            if reff_data.get("success"):
                self.log("🎉 Referral Benefit Claimed Successfully!", Fore.GREEN)
            else:
                self.log("❌ Failed to claim referral benefit: Success flag is False.", Fore.RED)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error while claiming referral benefit: {e}", Fore.RED)
            self.log(f"📄 Response Content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error: Unable to process referral benefit details: {e}", Fore.RED)
            self.log(f"📄 Response Content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error occurred: {e}", Fore.RED)
            self.log(f"📄 Response Content: {response.text if 'response' in locals() else 'No response'}", Fore.RED)

    def mastermind(self) -> None:
        headers = {**self.HEADERS, "authorization": self.token}

        # 1. Ambil data level dari endpoint mini-game-paws/level
        req_url_level = f"{self.BASE_URL}mini-game-paws/level"
        try:
            self.log("🚀 Fetching level details...", Fore.CYAN)
            response_level = requests.get(req_url_level, headers=headers)
            if response_level.status_code != 200:
                self.log(f"⚠️  Gagal mengambil detail level. Status Code: {response_level.status_code}", Fore.RED)
                self.log(f"📄 Response: {response_level.text}", Fore.CYAN)
                return

            level_data = response_level.json()
            self.log("🎮 Level Details:", Fore.GREEN)

            player = level_data.get("player", {})
            level = level_data.get("level", {})

            self.log(f"👤 User ID        : {player.get('userId', 'Unknown')}", Fore.YELLOW)
            self.log(f"🏆 Current Level  : {player.get('currentLevel', 'Unknown')}", Fore.YELLOW)
            self.log(f"🎯 Daily Moves    : {player.get('dailyMoves', 'Unknown')}", Fore.YELLOW)
            self.log("----- Level Info -----", Fore.YELLOW)
            self.log(f"🆔 Level ID       : {level.get('id', 'Unknown')}", Fore.YELLOW)
            self.log(f"🎚️ Level          : {level.get('level', 'Unknown')}", Fore.YELLOW)
            secret_length = level.get("secretLength", 0)
            self.log(f"🔑 Secret Length  : {secret_length}", Fore.YELLOW)

            rewards = level.get("rewards", [])
            if rewards:
                for reward in rewards:
                    self.log(f"🏅 Reward - Type: {reward.get('type')} | Amount: {reward.get('amount')}", Fore.YELLOW)
            else:
                self.log("🚫 No rewards available.", Fore.YELLOW)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error saat mengambil detail level: {e}", Fore.RED)
            return
        except ValueError as e:
            self.log(f"❌ Data error: Gagal memproses detail level: {e}", Fore.RED)
            return
        except Exception as e:
            self.log(f"❌ Terjadi error yang tidak terduga: {e}", Fore.RED)
            return

        # 2. Ambil data moves dari endpoint mini-game-paws/moves
        req_url_moves = f"{self.BASE_URL}mini-game-paws/moves"
        try:
            self.log("🔍 Fetching moves info...", Fore.CYAN)
            response_moves = requests.get(req_url_moves, headers=headers)
            if response_moves.status_code != 200:
                self.log(f"⚠️  Gagal mengambil moves info. Status Code: {response_moves.status_code}", Fore.RED)
                self.log(f"📄 Response: {response_moves.text}", Fore.CYAN)
                return

            moves_data = response_moves.json()
            daily_moves = moves_data.get("dailyMoves", 0)
            self.log("🎲 Moves Info:", Fore.GREEN)
            available = moves_data.get("available", {})
            self.log(f"🔢 Total Moves      : {available.get('total', 'Unknown')}", Fore.YELLOW)
            self.log(f"🔢 Daily Moves      : {daily_moves}", Fore.YELLOW)
            self.log(f"💎 Paid Moves       : {available.get('paid', 'Unknown')}", Fore.YELLOW)
            self.log(f"⏰ Daily Moves Cron : {moves_data.get('dailyMovesCron', 'Unknown')}", Fore.YELLOW)
            self.log(f"⏳ Next Reset At    : {moves_data.get('dailyMovesNextResetAt', 'Unknown')}", Fore.YELLOW)
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error saat mengambil moves info: {e}", Fore.RED)
            return
        except ValueError as e:
            self.log(f"❌ Data error: Gagal memproses moves info: {e}", Fore.RED)
            return
        except Exception as e:
            self.log(f"❌ Terjadi error yang tidak terduga: {e}", Fore.RED)
            return

        # 3. Mempersiapkan pencarian kombinasi dengan benar
        # Karena secret_length menentukan jumlah angka yang harus dimasukkan,
        # kita buat generator untuk semua kemungkinan kombinasi.
        perm_gen = itertools.permutations(range(secret_length))
        req_url_verify = f"{self.BASE_URL}mini-game-paws/stage/verify"
        attempt_counter = 0

        # Loop selama daily_moves mencukupi (minimal sama dengan secret_length)
        while daily_moves >= secret_length:
            attempt_counter += 1
            try:
                current_guess = next(perm_gen)
            except StopIteration:
                self.log("🚫 Semua kombinasi telah dicoba.", Fore.YELLOW)
                break

            self.log(f"🔄 Attempt #{attempt_counter}: Verifying stage with guess: {list(current_guess)}", Fore.CYAN)
            payload = {"secrets": list(current_guess)}

            try:
                response_verify = requests.post(req_url_verify, headers=headers, json=payload)
                if response_verify.status_code != 200:
                    self.log(f"⚠️  Gagal melakukan verify stage. Status Code: {response_verify.status_code}", Fore.RED)
                    self.log(f"📄 Response: {response_verify.text}", Fore.CYAN)
                    break

                verify_data = response_verify.json()
                self.log("🔍 Verify Response:", Fore.GREEN)
                self.log(f"✅ Success: {verify_data.get('success')}", Fore.YELLOW)

                attempts_list = verify_data.get("attempts", [])
                if attempts_list:
                    for idx, attempt in enumerate(attempts_list, start=1):
                        self.log(f"📝 Attempt {idx}:", Fore.CYAN)
                        self.log(f"   🔑 Secrets: {attempt.get('secrets')}", Fore.YELLOW)
                        self.log(f"   ✅ Result : {attempt.get('result')}", Fore.YELLOW)

                    # Cek kombinasi dari attempt terakhir.
                    # Misalnya, jika "result" adalah [False, False, ..., False] berarti kombinasi benar.
                    last_attempt = attempts_list[-1]
                    if last_attempt.get("result") == [False] * secret_length:
                        self.log("🎉 Kombinasi benar ditemukan!", Fore.GREEN)
                        break
                else:
                    self.log("⚠️ Tidak ada attempt yang ditemukan di verify response.", Fore.YELLOW)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Network error saat verify stage: {e}", Fore.RED)
                break
            except ValueError as e:
                self.log(f"❌ Data error: Gagal memproses verify response: {e}", Fore.RED)
                break
            except Exception as e:
                self.log(f"❌ Terjadi error yang tidak terduga: {e}", Fore.RED)
                break

            # Perbarui jumlah daily moves setelah tiap percobaan
            try:
                response_moves = requests.get(req_url_moves, headers=headers)
                if response_moves.status_code != 200:
                    self.log(f"⚠️  Gagal memperbarui moves info. Status Code: {response_moves.status_code}", Fore.RED)
                    self.log(f"📄 Response: {response_moves.text}", Fore.CYAN)
                    break

                moves_data = response_moves.json()
                daily_moves = moves_data.get("dailyMoves", 0)
                self.log(f"🔄 Updated Daily Moves: {daily_moves}", Fore.CYAN)
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Network error saat memperbarui moves info: {e}", Fore.RED)
                break
            except ValueError as e:
                self.log(f"❌ Data error: Gagal memproses updated moves info: {e}", Fore.RED)
                break
            except Exception as e:
                self.log(f"❌ Terjadi error yang tidak terduga: {e}", Fore.RED)
                break

            if daily_moves < secret_length:
                self.log("🚫 Daily moves tidak mencukupi untuk melanjutkan.", Fore.YELLOW)
                break

if __name__ == "__main__":
    cat = hashcat()
    index = 0
    max_index = len(cat.query_list)
    config = cat.load_config()

    cat.log("🎉 [LIVEXORDS] === Welcome to HashCat Automation === [LIVEXORDS]", Fore.YELLOW)
    cat.log(f"📂 Loaded {max_index} accounts from query list.", Fore.YELLOW)

    while True:
        current_account = cat.query_list[index]
        display_account = current_account[:10] + "..." if len(current_account) > 10 else current_account

        cat.log(f"👤 [ACCOUNT] Processing account {index + 1}/{max_index}: {display_account}", Fore.YELLOW)

        cat.login(index)

        cat.log("🛠️ Starting task execution...")
        tasks = {
            "daily": "🌞 Daily Check-In",
            "card": "💳 Card Collection",
            "tap": "🖱️ Tap Actions",
            "farm": "🌾 Farming",
            "stack_balance": "⬆️ Stacking Balance",
            "reff": "🤝 Referral Program",
            "mastermind": "mastermind solve",
        }

        for task_key, task_name in tasks.items():
            task_status = config.get(task_key, False)
            cat.log(f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}", Fore.YELLOW if task_status else Fore.RED)

            if task_status:
                cat.log(f"🔄 Executing {task_name}...")
                getattr(cat, task_key)()

        if index == max_index - 1:
            cat.log("🔁 All accounts processed. Restarting loop.")
            cat.log(f"⏳ Sleeping for {config.get('delay_loop', 30)} seconds before restarting.")
            time.sleep(config.get("delay_loop", 30))
            index = 0
        else:
            cat.log(f"➡️ Switching to the next account in {config.get('delay_account_switch', 10)} seconds.")
            time.sleep(config.get("delay_account_switch", 10))
            index += 1