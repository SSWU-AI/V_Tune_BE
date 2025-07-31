import os
import requests
import base64
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def tts_view(request):
    if request.method == 'POST':
        text = request.POST.get("text", "")
        if not text:
            return JsonResponse({"error": "text가 비어있습니다."}, status=400)

        api_key = settings.GOOGLE_TTS_API_KEY
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
        body = {
            "input": {"text": text},
            "voice": {"languageCode": "ko-KR", "ssmlGender": "NEUTRAL"},
            "audioConfig": {"audioEncoding": "MP3"}
        }

        res = requests.post(url, json=body)
        data = res.json()

        if "audioContent" in data:
            mp3_binary = base64.b64decode(data["audioContent"])
            return HttpResponse(mp3_binary, content_type="audio/mpeg")

        return JsonResponse({"error": data.get("error", "TTS 실패")}, status=500)

    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)
