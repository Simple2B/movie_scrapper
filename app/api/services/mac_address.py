import random, re
import subprocess as sub

from app.logging import logger


class MacAddress:
    # Function to generate a random MAC Address
    def get_random_mac_address(self):
        characters = "0123456789abcdef"
        random_mac_address = "00"
        for _ in range(5):
            random_mac_address += (
                ":" + random.choice(characters) + random.choice(characters)
            )
        return random_mac_address

    def change_mac(self, interface, new_mac):
        if len(new_mac) != 17:
            logger.error("[-] Please enter a valid MAC Address")
            quit()

        logger.info("[+] Changing the MAC Address to", new_mac)
        sub.call(["sudo", "ifconfig", interface, "down"])
        sub.call(["sudo", "ifconfig", interface, "hw", "ether", new_mac])
        sub.call(["sudo", "ifconfig", interface, "up"])

    def get_current_mac(self, interface):
        output = sub.check_output(["ifconfig", interface], universal_newlines=True)
        search_mac = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", output)
        if search_mac:
            return search_mac.group(0)
        else:
            logger.error("[-] Could not read the MAC Address")

    def mac_address(self, interface):
        try:
            prev_mac = self.get_current_mac(interface)
        except:
            logger.error("Wrong interface!")
            quit()
        logger.info("[+] MAC Address before change -> {}".format(prev_mac))
        new_mac = self.get_random_mac_address()
        self.change_mac(interface, new_mac)
        changed_mac = self.get_current_mac(interface)
        logger.info("[+] MAC Address after change -> {}".format(changed_mac))
        if changed_mac == new_mac:
            logger.info(
                "[+] MAC Address was successfully changed from {} to {}".format(
                    prev_mac, changed_mac
                )
            )
        else:
            logger.error("[-] Could not change the MAC Address")
