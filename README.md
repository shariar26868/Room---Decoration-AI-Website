# 🏠 Room Designer AI

AI-powered interior design platform with furniture search and visualization.

## 🌟 Features

- **Room Image Upload** - Upload photos of your room
- **Smart Room Analysis** - AI analyzes room dimensions and structure
- **Theme Selection** - Choose from 5 professional design themes
- **Furniture Search** - Search furniture from 50+ curated websites
- **Auto Dimension Calculation** - Automatic space planning
- **AI Visualization** - Generate realistic room designs with Stable Diffusion
- **AWS S3 Storage** - Secure cloud storage for images

## 🎨 Design Themes

1. **Minimal Scandinavian** - Clean lines, natural materials
2. **Timeless Luxury** - Elegant, sophisticated design
3. **Modern Living** - Contemporary and sleek
4. **Modern Mediterranean** - Warm, earthy tones
5. **Boho Eclectic** - Mix of patterns and textures

## 📋 Prerequisites

- Python 3.9+
- AWS Account (for S3 storage)
- Replicate API Key (for AI image generation)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd room-designer-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```env
REPLICATE_API_TOKEN=your_replicate_token
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

### 4. Setup AWS S3
```bash
python setup_aws.py
```

### 5. Test Configuration
```bash
python test_aws.py
```

### 6. Run Application
```bash
python main.py
```

Visit: http://localhost:8000/docs

## 📖 API Documentation

### Workflow

1. **POST** `/api/upload/upload` - Upload room image
2. **POST** `/api/selection/room-type` - Select room type
3. **POST** `/api/selection/theme` - Select design theme
4. **POST** `/api/selection/dimensions` - Enter room dimensions
5. **POST** `/api/selection/furniture/select` - Select furniture
6. **POST** `/api/furniture/price-range` - Set price range
7. **POST** `/api/furniture/search` - Search furniture
8. **POST** `/api/generation/generate` - Generate design image

### Example: Upload Room Image
```bash
curl -X POST "http://localhost:8000/api/upload/upload" \
  -F "room_image=@room.jpg"
```

Response:
```json
{
  "success": true,
  "image_url": "https://bucket.s3.amazonaws.com/rooms/...",
  "session_id": "uuid-here",
  "message": "Room image uploaded successfully"
}
```

## 🏗️ Project Structure