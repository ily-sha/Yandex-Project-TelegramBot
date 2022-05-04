from requests import post
import json
import base64

# Функция возвращает IAM-токен для аккаунта на Яндексе.
def get_iam_token(iam_url, oauth_token):
    response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
    json_data = json.loads(response.text)
    if json_data is not None and 'iamToken' in json_data:
        return json_data['iamToken']
    return None



def request_analyze(vision_url, iam_token, folder_id, image_data, l):
    print(l)
    response = post(vision_url, headers={'Authorization': 'Bearer '+iam_token}, json={
        'folderId': folder_id,
        'analyzeSpecs': [
            {
                'content': image_data,
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'textDetectionConfig': {'languageCodes': ["*"]}
                    }
                ],
            }
        ]})
    return response.json()


def main(photo, l):
    folder_id = "b1g5u5m7r4npnaaehf6t"
    iam_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    iam_token = get_iam_token(iam_url, "AQAAAAAucT-7AATuwc8zQM_S2UL8nE93deTk6v0")
    image_data = base64.b64encode(photo).decode('utf-8')
    response_text = request_analyze(vision_url, iam_token, folder_id, image_data, l)
    arr = []
    for f in response_text["results"]:
        for i in f["results"]:
            for j in i["textDetection"]["pages"]:
                for h in j["blocks"]:
                    for a in h["lines"]:
                        for w in a["words"]:
                            arr.append(w["text"])
    return " ".join(arr)