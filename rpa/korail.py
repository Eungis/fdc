import slack
import time
import os
from datetime import datetime
from korail2 import *

KORAIL_ID = os.environ["KORAIL_ID"]
KORAIL_PW = os.environ["KORAIL_PW"]
SLACK_TOKEN= os.environ["SLACK_TOKEN"]

slack_bot = slack.WebClient(token=SLACK_TOKEN)

korail = Korail(KORAIL_ID, KORAIL_PW, auto_login=False)
korail.login()

trial = 0
is_reserved = False
while not is_reserved:
    trial += 1
    print(f"========= {trial}-th reservation ========= ")
    
    try:
        if korail.logined:
            print("Profile logined: ", vars(korail))
        else:
            korail.login()
            print("Login success")

        def search_trains_with_no_error(*search_args, **search_kwargs):
            try:
                return korail.search_train(*search_args, **search_kwargs)
            except Exception as e:
                print(f"No trains found: {e}")
                return []

        # trains list
        seoul_trains, sejong_trains = [], []

        # search heading for seoul
        arrs = ["서울", "용산"]
        for arr in arrs:
            seoul_trains.extend(
                search_trains_with_no_error(
                    "여수EXPO",
                    arr,
                    "20241027",
                    "140000",
                    passengers=[AdultPassenger()],
                    include_no_seats=False,
                    train_type="100"
                )
            )

        # search heading for sejoing
        arrs = ["오송"]
        for arr in arrs:
            sejong_trains.extend(
                search_trains_with_no_error(
                    "여수EXPO",
                    arr,
                    "20241027",
                    "140000",
                    passengers=[AdultPassenger()],
                    include_no_seats=False,
                    train_type="100"
                )
            )
            
        # To get trains together
        pairs = []
        for seoul_train in seoul_trains:
            dpt_hour = datetime.strptime(seoul_train.dep_time, "%H%M%S").hour
            if not (dpt_hour >= 14 and dpt_hour < 19):
                continue
            
            _sejong_train = None
            for sejong_train in sejong_trains:
                if sejong_train.dep_time == seoul_train.dep_time:
                    _sejong_train = sejong_train
                    break
                
            if _sejong_train is not None:
                pairs += [(seoul_train, _sejong_train)]

        pairs = sorted(pairs, key=lambda x: x[0].dep_time)
        print(f"Number of matched pairs: {len(pairs)}")

        # Make reservation
        for seoul_train, sejong_train in pairs:
            if seoul_train.reserve_possible == "Y" and sejong_train.reserve_possible == "Y":
                print(
                    f"""\n
                    Available: {seoul_train}
                    Available: {sejong_train}
                    """
                )
                korail.reserve(seoul_train)
                korail.reserve(sejong_train)
                
                msg = f"Reservation Succeed!!\nHeading to Seoul: {seoul_train}\n\nHeading to Sejong: {sejong_train}"
                slack_bot.chat_postMessage(channel="#korail2", text=msg)
                is_reserved = True
                break
        time.sleep(5)
        
    except Exception as e:
        msg = f"***** Error raised during process: {e} *****"
        slack_bot.chat_postMessage(channel="#korail2", text=msg)
        continue

