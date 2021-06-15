# DICOMCropper

<H2> 개요 </H2>
HAND 파트를 촬영한 DCM파일을 로드해 좌수와 우수를 분류해 저장하는 프로그램입니다.

PyQT5, CV2를 기반으로 작성되었습니다.

<H2> 사용법 </H2>
1. service.py를 실행, 혹은 Pyinstaller를 이용해 exe파일로 변환 후 사용합니다.<br>
2. 입력 폴더 경로와 출력 폴더 경로를 설정하고 작업 시작을 누릅니다.<br>
3. dcm파일만 추출해 작업이 진행됩니다. 하단의 프로그레스 바 혹은 출력 메시지를 통해 진행상황을 알 수 있습니다.<br>

<H2> 예시 </H2>
<image src="https://user-images.githubusercontent.com/43870121/121974245-f3ed6f80-cdb9-11eb-9fcb-0d445c8e135d.png">
- 위와 같은 이미지가 존재 할 경우 아래와 같이 분류됩니다.<br>
- 왼손 예시<br>
<image src="https://user-images.githubusercontent.com/43870121/121974853-4713f200-cdbb-11eb-9e1b-768e1eec84e3.png">
- 오른손 예시<br>
<image src="https://user-images.githubusercontent.com/43870121/121974879-585cfe80-cdbb-11eb-9fee-6c5c99f41edb.png">


<H2> 특징 </H2>
- R 표시만 인식해 좌수와 우수를 분류합니다. L표시는 아직 인식하지 못합니다.<br>
- 아래와 같이 binarization, labeling 과정을 거쳐 연산 후 margin 50을 가진 상태로 return 합니다.
<image src="https://user-images.githubusercontent.com/43870121/121976100-14b7c400-cdbe-11eb-9af0-851b53fbce60.png">


<H2> 출력 구조 </H2>
- 출력폴더 <br>
          ㄴ HAND_R --  R_file 1, ..., R_file n<br>
          ㄴ HAND_L --- L_file 1, ..., L_file n<br>
