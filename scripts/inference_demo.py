"""
Bangladeshi Taka Note Detection CLI Inference Demo

To run single image local CLI inference:
  python scripts/inference_demo.py --image path/to/image.jpg

To build the Docker image:
  docker build -t taka-note-detector .

To run the Docker container:
  docker run -d -p 8000:8000 --name taka-api taka-note-detector

To use the API endpoint:
  curl -X POST "http://localhost:8000/predict" -F "file=@path/to/image.jpg"
"""

import argparse
import json
import os
import sys
from PIL import Image

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.inference import draw_detections, run_inference


def main():
    parser = argparse.ArgumentParser(description="Run single image inference demo.")
    parser.add_argument("--image", type=str, required=True, help="Path to input image.")
    parser.add_argument(
        "--output",
        type=str,
        default="scripts/output_annotated.jpg",
        help="Path to save annotated output image.",
    )
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image not found at '{args.image}'")
        sys.exit(1)

    print(f"Loading image: {args.image}")
    image = Image.open(args.image).convert("RGB")

    print("Running inference...")
    detections = run_inference(image, confidence_threshold=args.conf)

    print("\n--- Detection Results ---")
    if not detections:
        print("No notes detected.")
    else:
        for i, det in enumerate(detections, 1):
            print(f"{i}. Class: {det['class_name']}, Conf: {det['confidence']}, BBox: {det['bbox']}")

    print("\nRaw JSON Output:")
    print(json.dumps(detections, indent=2))

    annotated = draw_detections(image, detections)
    annotated.save(args.output)
    print(f"\nAnnotated image saved to: {args.output}")


if __name__ == "__main__":
    main()
