import requests
URL = "https://discord.com/api/webhooks/858974853516230706/-KMww3sv9nxZLR8xZS8TSzzxaZt_FMREP-_z6zN09TFVMwOzzsJvmfrwz8KD2EkIpUPb"

data = {"content": "Всё там воркает, гавно твой JS"}
response = requests.post(URL, json=data)
