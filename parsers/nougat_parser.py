import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from functools import partial
import torch
from tqdm import tqdm

try:
    from nougat import NougatModel
    from nougat.utils.device import move_to_device, default_batch_size
    from nougat.utils.checkpoint import get_checkpoint
    from nougat.postprocessing import markdown_compatible
    import pypdf
except ImportError as e:
    print("Nougat package is not installed. Please install nougat-ocr.")
    raise e

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NougatParser:
    def __init__(self, checkpoint: Optional[str] = None, model_tag: str = "0.1.0-base", batchsize: Optional[int] = None, full_precision: bool = False):
        self.batchsize = batchsize if batchsize is not None else default_batch_size()
        self.checkpoint = checkpoint or get_checkpoint(None, model_tag=model_tag)
        if self.checkpoint is None:
            raise RuntimeError("Could not find Nougat checkpoint. Please set NOUGAT_CHECKPOINT or download the model.")
        logger.info(f"Loading Nougat model from {self.checkpoint}")
        self.model = NougatModel.from_pretrained(self.checkpoint)
        self.model = move_to_device(self.model, bf16=not full_precision, cuda=self.batchsize > 0)
        if self.batchsize <= 0:
            self.batchsize = 1
        self.model.eval()

    def parse_pdf(self, pdf_path: str, output_path: Optional[str] = None, markdown: bool = True, recompute: bool = False, pages: Optional[list] = None) -> Dict[str, Any]:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        # Output path logic
        if output_path:
            output_path = Path(output_path)
            if output_path.suffix.lower() not in {".json", ".mmd", ".md"}:
                raise ValueError("Output path must end with .json, .mmd, or .md")
        # Prepare dataset
        from nougat.utils.dataset import LazyDataset  # Only import if available
        dataset = LazyDataset(
            pdf_path,
            partial(self.model.encoder.prepare_input, random_padding=False),
            pages,
        )
        import torch.utils.data
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=self.batchsize,
            shuffle=False,
            collate_fn=LazyDataset.ignore_none_collate,
        )
        predictions = []
        for i, (sample, is_last_page) in enumerate(tqdm(dataloader, desc=f"Parsing {pdf_path.name}")):
            model_output = self.model.inference(image_tensors=sample)
            for j, output in enumerate(model_output["predictions"]):
                if markdown:
                    output = markdown_compatible(output)
                predictions.append(output)
        # Join predictions
        full_text = "\n\n".join(predictions).strip()
        # Save output
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.suffix.lower() == ".json":
                result = {
                    "pdf": str(pdf_path),
                    "model": str(self.checkpoint),
                    "num_pages": len(predictions),
                    "text": full_text,
                }
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(full_text)
        return {"text": full_text, "num_pages": len(predictions)}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Nougat PDF Parser (latest)")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_path", help="Path to output file (.json, .mmd, or .md)")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to Nougat checkpoint directory")
    parser.add_argument("--model-tag", type=str, default="0.1.0-base", help="Model tag (default: 0.1.0-base)")
    parser.add_argument("--batchsize", type=int, default=None, help="Batch size (default: auto)")
    parser.add_argument("--full-precision", action="store_true", help="Use float32 instead of bfloat16")
    parser.add_argument("--no-markdown", action="store_true", help="Do not postprocess as markdown")
    args = parser.parse_args()
    parser_obj = NougatParser(
        checkpoint=args.checkpoint,
        model_tag=args.model_tag,
        batchsize=args.batchsize,
        full_precision=args.full_precision,
    )
    result = parser_obj.parse_pdf(
        args.input_pdf,
        args.output_path,
        markdown=not args.no_markdown,
    )
    print(f"Parsed {result['num_pages']} pages. Output saved to {args.output_path}")

if __name__ == "__main__":
    main() 