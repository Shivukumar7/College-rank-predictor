#!/usr/bin/env python3
"""
PDF Layout Extractor and Semantic Blocker
==========================================
This script extracts text and bounding boxes from a PDF document using `pdfplumber`,
groups the text into logical blocks (paragraphs, headers, list-items, etc.) based
on spatial proximity (coordinates), and outputs the structured layout in JSON format.

Dependencies:
    pip install pdfplumber

Usage:
    python pdf_layout_extractor.py input.pdf output.json
"""

import sys
import json
import os
from typing import List, Dict, Any, Tuple
import pdfplumber

class PDFLayoutExtractor:
    def __init__(self, x_gap_threshold: float = 15.0, y_gap_multiplier: float = 1.6, y_overlap_threshold: float = 0.5):
        """
        Initialize the extractor with threshold parameters for spatial grouping.
        
        :param x_gap_threshold: Max horizontal distance between words to keep them on the same line segment.
        :param y_gap_multiplier: Multiplier of line height to determine if consecutive lines belong to the same block.
        :param y_overlap_threshold: Minimum vertical overlap ratio to group words into the same line.
        """
        self.x_gap_threshold = x_gap_threshold
        self.y_gap_multiplier = y_gap_multiplier
        self.y_overlap_threshold = y_overlap_threshold

    def extract_layout(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts pages and segments them into structured semantic blocks.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Input PDF file not found: {pdf_path}")

        results = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_data = {
                    "page_number": page_idx + 1,
                    "width": float(page.width),
                    "height": float(page.height),
                    "blocks": []
                }

                # 1. Extract raw words
                words = page.extract_words()
                if not words:
                    results.append(page_data)
                    continue

                # 2. Group words into line segments (handling multi-column or inline gaps)
                lines = self._group_words_into_lines(words)

                # 3. Group line segments into larger logical blocks
                blocks = self._group_lines_into_blocks(lines)

                # 4. Classify blocks and calculate page-level stats
                classified_blocks = self._classify_blocks(blocks, page.height)

                # 5. Sort blocks in reading order
                sorted_blocks = self._sort_blocks_reading_order(classified_blocks)

                page_data["blocks"] = sorted_blocks
                results.append(page_data)

        return results

    def _group_words_into_lines(self, words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups words into line segments based on vertical overlap and horizontal proximity.
        """
        # Sort words primarily by top position, secondarily by x0
        sorted_words = sorted(words, key=lambda w: (w["top"], w["x0"]))
        
        raw_lines: List[List[Dict[str, Any]]] = []
        
        for word in sorted_words:
            placed = False
            # Try to place word in an existing raw line based on vertical overlap
            for line in raw_lines:
                # Reference vertical boundaries of the line
                line_top = min(w["top"] for w in line)
                line_bottom = max(w["bottom"] for w in line)
                line_height = line_bottom - line_top
                
                # Word boundaries
                w_top = word["top"]
                w_bottom = word["bottom"]
                w_height = w_bottom - w_top
                
                # Compute overlap
                overlap = min(line_bottom, w_bottom) - max(line_top, w_top)
                min_h = min(line_height, w_height)
                
                if min_h > 0 and (overlap / min_h) >= self.y_overlap_threshold:
                    line.append(word)
                    placed = True
                    break
            
            if not placed:
                raw_lines.append([word])

        # Now split raw lines into segments if there are wide horizontal gaps (multi-column)
        line_segments = []
        for line_words in raw_lines:
            line_words.sort(key=lambda w: w["x0"])
            
            current_segment = [line_words[0]]
            for word in line_words[1:]:
                prev_word = current_segment[-1]
                # If the gap between words is larger than the threshold, split the line
                if (word["x0"] - prev_word["x1"]) > self.x_gap_threshold:
                    line_segments.append(current_segment)
                    current_segment = [word]
                else:
                    current_segment.append(word)
            line_segments.append(current_segment)

        # Structure the line segments with text and bounding box
        structured_lines = []
        for segment in line_segments:
            x0 = min(w["x0"] for w in segment)
            top = min(w["top"] for w in segment)
            x1 = max(w["x1"] for w in segment)
            bottom = max(w["bottom"] for w in segment)
            text = " ".join(w["text"] for w in segment)
            
            structured_lines.append({
                "bbox": [float(x0), float(top), float(x1), float(bottom)],
                "text": text,
                "height": float(bottom - top),
                "words": [{"text": w["text"], "bbox": [float(w["x0"]), float(w["top"]), float(w["x1"]), float(w["bottom"])]} for w in segment]
              })
              
        return structured_lines

    def _group_lines_into_blocks(self, lines: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Groups line segments into larger blocks based on spatial proximity.
        """
        # Sort lines by top coordinate
        sorted_lines = sorted(lines, key=lambda l: (l["bbox"][1], l["bbox"][0]))
        blocks: List[List[Dict[str, Any]]] = []

        for line in sorted_lines:
            placed = False
            l_x0, l_top, l_x1, l_bottom = line["bbox"]
            l_height = line["height"]

            # Try to place in an existing block
            for block in blocks:
                # Get block boundaries
                b_x0 = min(item["bbox"][0] for item in block)
                b_top = min(item["bbox"][1] for item in block)
                b_x1 = max(item["bbox"][2] for item in block)
                b_bottom = max(item["bbox"][3] for item in block)
                
                # Check vertical proximity
                vertical_gap = l_top - b_bottom
                max_allowed_gap = max(l_height, (b_bottom - b_top) / len(block)) * self.y_gap_multiplier

                # Check horizontal overlap
                overlap_x = min(l_x1, b_x1) - max(l_x0, b_x0)
                min_width = min(l_x1 - l_x0, b_x1 - b_x0)
                has_x_overlap = (overlap_x > 0) or (abs(l_x0 - b_x0) < self.x_gap_threshold)

                # If the line is close below the block and shares horizontal space, group them
                if 0 <= vertical_gap <= max_allowed_gap and has_x_overlap:
                    block.append(line)
                    placed = True
                    break

            if not placed:
                blocks.append([line])

        return blocks

    def _classify_blocks(self, blocks: List[List[Dict[str, Any]]], page_height: float) -> List[Dict[str, Any]]:
        """
        Classifies each block into categories: header, footer, list-item, paragraph, or other.
        """
        # Calculate median line height to determine the "standard" body font size
        all_heights = [line["height"] for block in blocks for line in block]
        all_heights.sort()
        median_height = all_heights[len(all_heights) // 2] if all_heights else 10.0

        classified = []
        for idx, block in enumerate(blocks):
            b_x0 = min(line["bbox"][0] for line in block)
            b_top = min(line["bbox"][1] for line in block)
            b_x1 = max(line["bbox"][2] for line in block)
            b_bottom = max(line["bbox"][3] for line in block)
            
            # Combine text
            text = "\n".join(line["text"] for line in block)
            
            # Determine type
            block_type = "paragraph"
            first_line_text = block[0]["text"].strip()
            
            # 1. Header/Footer margin check
            if b_top < page_height * 0.07:
                block_type = "header-margin"
            elif b_bottom > page_height * 0.93:
                block_type = "footer"
            # 2. Heading check (larger font size / line height, few lines)
            elif len(block) <= 2 and block[0]["height"] > median_height * 1.25:
                block_type = "heading"
            # 3. List item check
            elif (first_line_text.startswith(("- ", "• ", "* ")) or 
                  (first_line_text.split(".")[0].isdigit() and len(first_line_text.split(".")) > 1)):
                block_type = "list-item"

            classified.append({
                "id": f"block_{idx}",
                "type": block_type,
                "bbox": [float(b_x0), float(b_top), float(b_x1), float(b_bottom)],
                "text": text,
                "lines": block
            })

        return classified

    def _sort_blocks_reading_order(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts blocks in reading order, handling multi-column layouts correctly.
        """
        # Simple column-based sorting:
        # We group blocks that overlap horizontally, creating column channels.
        if not blocks:
            return []

        # Sort left-to-right first to identify potential columns
        sorted_by_x = sorted(blocks, key=lambda b: b["bbox"][0])
        columns: List[List[Dict[str, Any]]] = []

        for block in sorted_by_x:
            placed = False
            b_x0, _, b_x1, _ = block["bbox"]
            
            for col in columns:
                # If there's significant horizontal overlap with this column, add to it
                col_x0 = min(b["bbox"][0] for b in col)
                col_x1 = max(b["bbox"][2] for b in col)
                overlap = min(b_x1, col_x1) - max(b_x0, col_x0)
                if overlap > 0:
                    col.append(block)
                    placed = True
                    break
            
            if not placed:
                columns.append([block])

        # Sort each column top-to-bottom
        for col in columns:
            col.sort(key=lambda b: b["bbox"][1])

        # Re-sort columns left-to-right by their average x0 position
        columns.sort(key=lambda col: sum(b["bbox"][0] for b in col) / len(col))

        # Flatten list
        sorted_blocks = [block for col in columns for block in col]
        return sorted_blocks

def main():
    if len(sys.argv) < 3:
        print("Usage: python pdf_layout_extractor.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Extracting layout from: {pdf_path}...")
    extractor = PDFLayoutExtractor()
    try:
        data = extractor.extract_layout(pdf_path)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved structured JSON to: {output_path}")
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
