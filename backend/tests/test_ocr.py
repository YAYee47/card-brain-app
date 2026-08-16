import asyncio
from app.services.ocr import analyze_image_with_gemini

async def main():
    image_path = "C:/Users/kitty/.gemini/antigravity/brain/3b155dd8-6857-4c93-8133-76e96b302a72/.user_uploaded/media_1786641571079.png"
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except Exception as e:
        print("Failed to read image:", e)
        return
        
    res = await analyze_image_with_gemini(image_bytes, "image/png")
    print("OCR RESULT:")
    print(res.model_dump())

if __name__ == "__main__":
    asyncio.run(main())
