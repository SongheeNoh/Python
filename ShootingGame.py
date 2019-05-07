import pygame
import random
import sys
import time


## 함수 선언 부분 ##
# @기능 : 기존에 있던 기능이다.
# @@기능 : 내가 추가한 기능이다.

# @기능 : 매개변수로 받은 객체를 화면에 그리는 함수를 선언한다.
def paintEntiry(entity, x, y):
    monitor.blit(entity, (x, y))


# @@기능 : 사각형 안에서 텍스트를 줄바꿔 출력하는 코드, 구글링하여 오픈소스를 따옴, 나중에 보고 제대로 이해할 것
class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, justification=0):
    final_lines = []
    requested_lines = string.splitlines()

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException + "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException + "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException + "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface


# @@기능 : 게임설명을 화면에 띄우는 함수를 선언
def writeInfo():
    infoRect = pygame.Rect(50, 100, 400, 450)
    myfont = pygame.font.Font('NanumGothic.ttf', 20)  # 한글 폰트
    explain = "\n            <우주괴물 무찌르기 게임설명>\n\n" \
              "\t\t방향키로 우주선을 조종하고 space bar를 \t\t누르면 발사되는 미사일로 떨어지는 \t\t우주괴물을 맞혀주세요!!!" \
              "\n\n   * 주어진 목숨은 단 세 개!" \
              "\n   * 우주괴물과 우주선이 닿으면 목숨이 한 \t\t\t\t\t\t개씩 줄어들어요!" \
              "\n   * 우주괴물이 창 너머로 사라지면 점수가 \t\t\t\t\t\t1점씩 줄어들어요!" \
              "\n\n\t\t목숨이 다 사라지기 전에 10점을 달성하여 \t\t우주괴물로부터 탈출하세요!!!" \
              "\n\n\t\t\t-----이 창은 5초 후에 저절로 닫힙니다-----"
    # 줄바꿈 함수 포함된 사각형 띄우기
    infoText = render_textrect(explain, myfont, infoRect, (216, 216, 216), (48, 48, 48), 0)
    monitor.blit(infoText, infoRect.topleft)


# @기능 : 점수를 화면에 쓰는 함수를 선언
def writeScore(score):
    myfont = pygame.font.Font('NanumGothic.ttf', 20)  # 한글 폰트
    txt = myfont.render(u'파괴한 우주괴물 수 : ' + str(score), True, (255 - r, 255 - g, 255 - b))
    monitor.blit(txt, (10, sheight - 40))


# @@기능 : 결과를 화면에 쓰는 함수를 선언
def writeResult(result):
    myfont = pygame.font.Font('HoboStd.otf', 50)  # 영문 폰트
    # @@기능 : 점수가 10점이 넘으면 WIN 표시, 그 전에 목숨이 다 닳으면 LOSE 표시
    if fireCount >= 10:
        result = myfont.render(u'YOU WIN!!!', True, (255 - r, 255 - g, 255 - b))
        monitor.blit(result, (120, sheight / 2))
    elif life == 0:
        result = myfont.render(u'YOU LOSE..', True, (255 - r, 255 - g, 255 - b))
        monitor.blit(result, (120, sheight / 2))


def playGame():
    global monitor, ship, monster, missile, life, fireCount

    # @기능 : 우주선의 초기 위치와 키보드를 눌렀을 때 이동량을 선언한다.
    shipX = swidth / 2  # 우주선 위치
    shipY = sheight * 0.7
    dx, dy = 0, 0  # 키보드를 누를때 우주선의 이동량


    # @기능 : (처음 나올) 우주괴물을 랜덤하게 추출하고 크기와 위치를 설정
    monster = pygame.image.load(random.choice(monsterImage))
    monsterSize = monster.get_rect().size  # 우주괴물 크기
    monsterX = random.randrange(0, int(swidth - shipSize[1]))
    monsterY = 0
    monsterSpeed = random.randrange(3, 7)


    # @기능 : 미사일 좌표를 초기화
    missileX, missileY = None, None  # None은 미사일을 쏘지 않았다는 의미


    # @@기능 : 게임설명 버튼 사각형
    infoButton = pygame.Rect(400, 20, 80, 30)
    myfont = pygame.font.Font('NanumGothic.ttf', 20)  # 한글 폰트


    # 무한 반복
    while True:
        (pygame.time.Clock()).tick(50)  # 게임 진행을 늦춘다(10~100 정도가 적당).
        monitor.fill((r, g, b))  # 화면 배경을 칠한다.

        # 키보드나 마우스 이벤트가 들어오는지 체크한다.
        for e in pygame.event.get():
            if e.type in [pygame.QUIT]:
                pygame.quit()
                sys.exit()


            # @@기능 : 게임설명 버튼을 누르면 게임설명 사각형이 뜨도록 함
            if e.type in [pygame.MOUSEBUTTONDOWN]:
                if e.button == 1:  # 1이 왼쪽 마우스, 2가 가운데 마우스, 3이 오른쪽 마우스
                    mouse_x, mouse_y = e.pos
                    if infoButton.collidepoint(mouse_x, mouse_y):  # 마우스 좌표가 게임설명 버튼을 클릭하면
                        writeInfo()
                        pygame.display.update()  # 디스플레이 업데이트 꼭 들어가야 함... 두 시간 고생한 원인...
                        time.sleep(5)  # 5초 동안 화면 멈춤


            # @기능 : 방향키에 따라 우주선이 움직이게 함
            # 방향키를 누르면 우주선이 이동한다(누르고 있으면 계속 이동).
            elif e.type in [pygame.KEYDOWN]:
                if e.key == pygame.K_LEFT:
                    dx = -5
                elif e.key == pygame.K_RIGHT:
                    dx = +5
                elif e.key == pygame.K_UP:
                    dy = -5
                elif e.key == pygame.K_DOWN:
                    dy = +5
                # @기능 4-3 : 스페이스바를 누르면 미사일을 발사한다.
                elif e.key == pygame.K_SPACE:
                    if missileX == None:  # 미사일을 쏜 적이 없다면
                        missileX = shipX + shipSize[0] / 2  # 우추선 위치에서 미사일을 발사한다.
                        missileY = shipY

            # 방향키를 떼면 우주선이 멈춘다.
            elif e.type in [pygame.KEYUP]:
                if e.key == pygame.K_LEFT or e.key == pygame.K_RIGHT \
                        or e.key == pygame.K_UP or e.key == pygame.K_DOWN: dx, dy = 0, 0


        # @기능 : 우주선이 화면 안에서만 움직이게 한다.
        if (0 < shipX + dx <= swidth - shipSize[0]) \
                and (shipY + dy > sheight / 2 <= sheight - shipSize[1]):  # 화면의 중앙까지만
            shipX += dx
            shipY += dy
        paintEntiry(ship, shipX, shipY)  # 우주선을 화면에 표시한다.


        # @@기능 : 우주괴물이 무작위 위치에서 위에서 아래로 내려옴
        monsterY += monsterSpeed

        if monsterY > sheight:
            monsterX = random.randrange(0, int(swidth - shipSize[1]))
            monsterY = 0
            # 우주괴물 이미지를 무작위로 선택한다.
            monster = pygame.image.load(random.choice(monsterImage))
            monsterSize = monster.get_rect().size
            monsterSpeed = random.randrange(3, 7)

        paintEntiry(monster, monsterX, monsterY)


        # @@기능 : 우주괴물이 살아서 바닥까지 도착하면 점수에서 1점을 뺌
        if monsterY == sheight:
            fireCount -= 1


        # @기능 : 미사일을 화면에 표시한다.
        if missileX != None:  # 총알을 쏘면 좌표를 위로 변경한다.
            missileY -= 10
            if missileY < 0:
                missileX, missileY = None, None  # 총알이 사라진다.

        if missileX != None:  # 미사일을 쏜 적이 있으면 미사일을 그려준다.
            paintEntiry(missile, missileX, missileY)
            # @기능 : 우주괴물이 미사일에 맞았는지 체크
            if (monsterX < missileX < monsterX + monsterSize[0]) and \
                    (monsterY < missileY < monsterY + monsterSize[1]):
                fireCount += 1

                # 우주괴물을 초기화(무작위 이미지로 다시 준비)
                monster = pygame.image.load(random.choice(monsterImage))
                monsterSize = monster.get_rect().size
                monsterX = random.randrange(0, int(swidth - shipSize[1]))
                monsterY = 0
                monsterSpeed = random.randrange(3, 7)

                # 미사일을 초기화한다.
                missileX, missileY = None, None  # 총알이 사라진다.


        # @@기능 : 우주선의 목숨을 3개로 설정하고 우주괴물과 닿을 때마다 1씩 줄어드는게 화면에 표시되게 함
        # 우주괴물이 우주선에 맞았는지 체크
        if (monsterX < shipX < monsterX + monsterSize[0]) and \
                (monsterY < shipY < monsterY + monsterSize[1]):
            life -= 1

            # 우주괴물을 초기화(무작위 이미지로 다시 준비)
            monster = pygame.image.load(random.choice(monsterImage))
            monsterSize = monster.get_rect().size
            monsterX = random.randrange(0, int(swidth - shipSize[1]))
            monsterY = 0
            monsterSpeed = random.randrange(3, 7)

            # 우주선을 초기화
            shipX = swidth / 2
            shipY = sheight * 0.7  # 우주선이 처음자리로 감

        # 화면에 표시되는 우주선 목숨
        shipLife = pygame.image.load('C:/images/ship01.png')  # 목숨도 우주선 모양으로
        shipLife = pygame.transform.scale(shipLife, (25, 44))  # 우주선 크기를 좀 더 작게 설정
        shipLife = pygame.transform.rotate(shipLife, -30)  # 목숨처럼 보이도록 각도를 조금 돌림
        for i in range(0, life):
            monitor.blit(shipLife, (385 + 35 * i, sheight - 55))


        # @기능 : 점수를 화면에 쓰는 함수를 호출
        writeScore(fireCount)
        # @@기능 : 결과를 화면에 쓰는 함수를 호출
        writeResult(result)


        # @@기능 : 게임설명 버튼 호출
        pygame.draw.rect(monitor, (255, 255, 255), infoButton)
        infoButtonText = myfont.render("게임설명", True, (0, 0, 0))
        monitor.blit(infoButtonText, infoButton)


        # 화면을 업데이트
        pygame.display.update()
        print('~', end='')


        # 점수가 30점이 되면 화면 업데이트 그만하도록
        if fireCount >= 10 or life == 0:
            break


    # @@기능 : 결과 화면을 5초간 멈춘 후 게임 화면 종료
    time.sleep(5)
    pygame.quit()


## 전역 변수 선언 부분 ##

swidth, sheight = 500, 700  # 화면 크기
monitor = None  # 게임 화면
ship, shipSize = None, 0  # 우주선의 객체와 크기 변수
life = 3  # @@ 우주선의 목숨
fireCount = 0  # 맞힌 우주괴물 숫자

shipLife = None  # @@기능 : 우주선 목숨그림
result = None  # 게임 결과

# 게임 배경색
r = random.randrange(0, 256)
g = random.randrange(0, 256)
b = random.randrange(0, 256)

# @기능 : 랜덤하게 사용할 우주괴물의 이미지 10개를 준비
monsterImage = ['C:/images/monster01.png', 'C:/images/monster02.png', 'C:/images/monster03.png', \
                'C:/images/monster04.png', 'C:/images/monster05.png', 'C:/images/monster06.png', \
                'C:/images/monster07.png', 'C:/images/monster08.png', 'C:/images/monster09.png', \
                'C:/images/monster10.png']
monster = None  # 우주괴물
missile = None  # 미사일

## 메인 코드 부분 ##
pygame.init()

# @@기능 : 배경음악 추가함
pygame.mixer.music.load('BGM.mp3')
pygame.mixer.music.play(-1, 0.0)  # (재생횟수, 시작시간) 재생횟수를 -1로 하면 무한반복

monitor = pygame.display.set_mode((swidth, sheight))
pygame.display.set_caption('우주괴물 무찌르기')

# @기능 : 우주선 이미지를 준비하고 크기를 구한다.
ship = pygame.image.load('C:/images/ship01.png')
shipSize = ship.get_rect().size

# @기능 : 미사일 이미지를 추가한다.
missile = pygame.image.load('C:/images/missile.png')

playGame()