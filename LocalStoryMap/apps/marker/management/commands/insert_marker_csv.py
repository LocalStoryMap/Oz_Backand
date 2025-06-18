import csv
import os

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.marker.models import Marker


class Command(BaseCommand):
    help = "CSV 파일을 읽어 Marker 데이터를 이미지와 함께 대량으로 삽입합니다."

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, "markers.csv")
        with open(csv_path, encoding="utf-8-sig") as f:  # BOM 처리용 인코딩
            reader = csv.DictReader(f)
            # 빈 컬럼명 제거
            reader.fieldnames = [name.strip() for name in reader.fieldnames if name]
            for row in reader:
                marker = Marker(
                    marker_name=row["제목"],
                    adress=row["주소"],
                    description=row["내용"],
                    latitude=float(row["위도"]) if row["위도"] else None,
                    longitude=float(row["경도"]) if row["경도"] else None,
                    layer=row["레이어"],
                )
                image_url = row["이미지주소"]
                if image_url:
                    try:
                        response = requests.get(image_url, timeout=10)
                        if response.status_code == 200:
                            # 파일명에서 확장자를 무조건 .jpg로 변경
                            base_name = os.path.basename(image_url)
                            if "." in base_name:
                                base_name = os.path.splitext(base_name)[0]
                            file_name = base_name + ".jpg"
                            marker.image.save(
                                file_name, ContentFile(response.content), save=False
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"이미지 다운로드 실패: {image_url} - {e}")
                        )
                marker.save()
        self.stdout.write(self.style.SUCCESS("데이터 입력 완료!"))
