from pdf2image import convert_from_path
from transformers import DonutProcessor, VisionEncoderDecoderModel
import torch
import re

# Load Donut model and processor
processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Convert PDF pages to images
pdf_path = "shared/input_pdfs/transcript.pdf"
images = convert_from_path(pdf_path)

# Process each page image
for i, image in enumerate(images):
    print(f"Processing page {i+1}/{len(images)}")

    # Prepare decoder input ids with task prompt
    task_prompt = "<s_cord-v2>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

    # Prepare pixel values
    pixel_values = processor(image, return_tensors="pt").pixel_values

    # Generate output sequence
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_position_embeddings,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )

    # Decode output sequence
    sequence = processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token

    # Convert sequence to JSON output
    json_output = processor.token2json(sequence)
    print(json_output)
