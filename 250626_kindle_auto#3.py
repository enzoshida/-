import pyautogui
import time
import os
import keyboard
import sys
from PIL import Image, ImageChops # ImageChopsに加えてImageもインポートする

# --- ここからプログラム本体 ---

def setup_save_directory():
    """
    デスクトップに画像を保存するためのフォルダを作成する。
    OneDriveと日本語環境を考慮して、デスクトップのパスを自動で探す。
    """
    possible_paths = [
        os.path.join(os.path.expanduser('~'), 'OneDrive', 'デスクトップ'),
        os.path.join(os.path.expanduser('~'), 'Desktop'),
        os.path.join(os.path.expanduser('~'), 'デスクトップ')
    ]
    desktop_path = ""
    for path in possible_paths:
        if os.path.exists(path):
            desktop_path = path
            break
    if not desktop_path:
        print("❌ エラー: デスクトップフォルダが見つかりませんでした。")
        return None

    while True:
        folder_name = input("デスクトップに作成する保存フォルダの名前を入力してください: ")
        if folder_name:
            break
        else:
            print("エラー: フォルダ名は空にできません。")
            
    save_dir = os.path.join(desktop_path, folder_name)
    try:
        os.makedirs(save_dir, exist_ok=True)
        print(f"\n✅ 画像を '{save_dir}' に保存します。")
        return save_dir
    except OSError as e:
        print(f"❌ フォルダの作成に失敗しました: {e}")
        return None

def get_capture_region():
    # この関数の内容は変更ありません
    print("\n--- 📖 撮影範囲の指定 ---")
    print("Kindleアプリを最前面に表示し、撮影したいページを開いてください。")
    input("準備ができたらEnterキーを押してください...")
    try:
        print("\n【1/2】 5秒後にマウスカーソルの位置を記録します...")
        print("     Kindle本のページの《左上》にマウスカーソルを合わせて、そのまま動かさないでください...")
        time.sleep(5)
        left_top = pyautogui.position()
        print(f"   -> 左上の座標を取得しました: {left_top}")
        print("\n【2/2】 もう一度、5秒後にマウスカーソルの位置を記録します...")
        print("     次はページの《右下》にマウスカーソルを合わせて、そのまま動かさないでください...")
        time.sleep(5)
        right_bottom = pyautogui.position()
        print(f"   -> 右下の座標を取得しました: {right_bottom}")
        width = right_bottom.x - left_top.x
        height = right_bottom.y - left_top.y
        if width <= 0 or height <= 0:
            print("\n❌ エラー: 範囲が正しくありません。")
            return None
        capture_region = (left_top.x, left_top.y, width, height)
        print(f"\n✅ 撮影範囲が設定されました: x={capture_region[0]}, y={capture_region[1]}, 幅={capture_region[2]}, 高さ={capture_region[3]}")
        return capture_region
    except Exception as e:
        print(f"❌ 座標の取得中にエラーが発生しました: {e}")
        return None

def are_images_same(img1: Image.Image, img2: Image.Image) -> bool:
    """2つの画像オブジェクトが同一か比較するヘルパー関数"""
    if img1 is None or img2 is None:
        return False
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is None

def main():
    print("--- 📖 Kindle自動スクリーンショットツール ---")
    # ... (注意事項の表示は変更なし) ...

    save_dir = setup_save_directory()
    if not save_dir: sys.exit()
    region = get_capture_region()
    if not region: sys.exit()

    print("\n--- 📸 撮影開始 ---")
    print("3秒後に撮影を開始します。")
    print("【‼️重要‼️】同じページが3回続くと自動で停止します。") # --- 表示メッセージを更新 ---
    print("     もし自動で停止しない場合は、保険として『q』キーを押し続けてください。")
    time.sleep(3)
    
    page_number = 1
    wait_time_after_page_turn = 0.8
    click_point_x = region[0] + region[2] // 2
    click_point_y = region[1] + region[3] // 2
    
    # --- 変更点：2つ前と1つ前の画像を保存する変数を準備 ---
    last_img = None
    second_to_last_img = None

    try:
        while True:
            if keyboard.is_pressed('q'):
                print("\n'q'キーが押されたため、手動で終了します。")
                break

            current_img = pyautogui.screenshot(region=region)
            
            # --- 変更点：自動停止アルゴリズムを3枚比較に変更 ---
            # 3枚の画像が揃っているか（Noneでないか）を確認
            if last_img is not None and second_to_last_img is not None:
                # 3枚の画像が連続で同じか判定
                if are_images_same(second_to_last_img, last_img) and are_images_same(last_img, current_img):
                    print(f"\n3ページ連続で同じ画像が検出されたため、撮影を自動で終了します。")
                    break
            # --- 変更点ここまで ---

            file_path = os.path.join(save_dir, f"{page_number}.png")
            current_img.save(file_path)
            print(f"ページ {page_number} を撮影しました。")
            
            # --- 変更点：比較のために画像を1つずつずらして保存 ---
            second_to_last_img = last_img
            last_img = current_img
            
            # ページめくり処理
            pyautogui.click(click_point_x, click_point_y)
            time.sleep(0.2)
            pyautogui.press('right') 
            
            page_number += 1
            time.sleep(wait_time_after_page_turn)

    except Exception as e:
        print(f"\n❌ 予期せぬエラーが発生しました: {e}")
    finally:
        print("\n--- 🎉 処理完了 ---")
        print(f"合計 {page_number - 1} 枚の画像を保存しました。") 
        print(f"保存先フォルダ: {save_dir}")

if __name__ == "__main__":
    main()