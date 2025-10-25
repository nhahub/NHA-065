"""
Model Manager for Zypher AI Logo Generator
Handles loading and managing Flux Schnell model with optional LoRA and IP-Adapter
"""
import torch
from diffusers import FluxPipeline
from PIL import Image
import os
from dotenv import load_dotenv
import config

# Load environment variables
load_dotenv()

class ModelManager:
    """Manages the Flux Schnell model, LoRA weights, and IP-Adapter"""
    
    def __init__(self):
        self.pipeline = None
        self.device = config.GPU_DEVICE if config.USE_GPU and torch.cuda.is_available() else "cpu"
        self.lora_loaded = False
        self.current_lora = None  # Track which LoRA is currently loaded
        self.base_model_loaded = False
        self.ip_adapter_loaded = False
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
    
    def get_available_loras(self):
        """Get list of available LoRA files in the lora directory"""
        lora_files = []
        try:
            if os.path.exists(config.LORA_MODEL_PATH):
                for file in os.listdir(config.LORA_MODEL_PATH):
                    if file.endswith('.safetensors'):
                        lora_files.append(file)
        except Exception as e:
            print(f"Error listing LoRA files: {e}")
        return sorted(lora_files)
        
    def load_base_model(self):
        """Load the base Flux Schnell model"""
        if self.base_model_loaded and self.pipeline is not None:
            print("Base model already loaded")
            return
            
        try:
            print(f"Loading Flux Schnell model on {self.device}...")
            
            # Check if token is available
            if not self.hf_token or self.hf_token == "your_huggingface_token_here":
                print("⚠️  WARNING: HUGGINGFACE_TOKEN not set in .env file")
                print("   Get your token from: https://huggingface.co/settings/tokens")
                print("   Attempting to download without authentication...")
            else:
                print("✓ Using Hugging Face authentication token")
            
            self.pipeline = FluxPipeline.from_pretrained(
                config.BASE_MODEL_ID,
                torch_dtype=torch.bfloat16 if self.device != "cpu" else torch.float32,
                token=self.hf_token if self.hf_token and self.hf_token != "your_huggingface_token_here" else None
            )
            self.pipeline.to(self.device)
            
            # Enable memory optimizations
            if self.device != "cpu":
                self.pipeline.enable_model_cpu_offload()
            
            self.base_model_loaded = True
            self.lora_loaded = False
            print("✓ Base model loaded successfully")
        except Exception as e:
            print(f"Error loading base model: {e}")
            if "gated" in str(e).lower() or "access" in str(e).lower():
                print("\n❌ Authentication Error!")
                print("   This model requires authentication. Please:")
                print("   1. Get your token from: https://huggingface.co/settings/tokens")
                print("   2. Add it to the .env file: HUGGINGFACE_TOKEN=your_token_here")
                print("   3. Accept the model's license at: https://huggingface.co/black-forest-labs/FLUX.1-schnell")
            raise
    
    def load_lora(self, lora_filename=None):
        """
        Load LoRA weights on top of the base model
        
        Args:
            lora_filename (str): Specific LoRA file to load. If None, uses config default.
        """
        if not self.base_model_loaded:
            self.load_base_model()
        
        # Use provided filename or default from config
        if lora_filename is None:
            lora_filename = config.LORA_WEIGHTS_FILE
        
        lora_path = os.path.join(config.LORA_MODEL_PATH, lora_filename)
        
        if not os.path.exists(lora_path):
            raise FileNotFoundError(
                f"LoRA weights not found at {lora_path}. "
                f"Please place your LoRA weights in the models/lora folder."
            )
        
        try:
            # Unload any existing LoRA first
            if self.lora_loaded:
                print(f"Unloading previous LoRA: {self.current_lora}")
                self.pipeline.unload_lora_weights()
            
            print(f"Loading LoRA weights: {lora_filename}...")
            # Load new LoRA weights
            self.pipeline.load_lora_weights(lora_path)
            self.lora_loaded = True
            self.current_lora = lora_filename
            print(f"✓ LoRA weights loaded successfully: {lora_filename} (scale: {config.LORA_SCALE})")
        except Exception as e:
            print(f"Error loading LoRA: {e}")
            self.lora_loaded = False
            self.current_lora = None
            raise
    
    def unload_lora(self):
        """Unload LoRA weights to use base model only"""
        if self.lora_loaded and self.pipeline is not None:
            try:
                print(f"Unloading LoRA weights: {self.current_lora}...")
                self.pipeline.unload_lora_weights()
                self.lora_loaded = False
                self.current_lora = None
                print("✓ LoRA weights unloaded, using base model")
            except Exception as e:
                print(f"Error unloading LoRA: {e}")
    
    def load_ip_adapter(self):
        """Load IP-Adapter for image-to-image conditioning"""
        if not self.base_model_loaded:
            self.load_base_model()
        
        if self.ip_adapter_loaded:
            print("IP-Adapter already loaded")
            return
        
        try:
            print("Loading IP-Adapter...")
            # Load IP-Adapter weights with authentication token
            self.pipeline.load_ip_adapter(
                "h94/IP-Adapter", 
                subfolder="models",
                weight_name="ip-adapter_sd15.bin",
                token=self.hf_token if self.hf_token and self.hf_token != "your_huggingface_token_here" else None
            )
            self.ip_adapter_loaded = True
            print("✓ IP-Adapter loaded successfully")
        except Exception as e:
            print(f"Note: IP-Adapter loading failed: {e}")
            print("Continuing without IP-Adapter support...")
            self.ip_adapter_loaded = False
    
    def generate_image(self, prompt, use_lora=False, lora_filename=None, reference_image=None, ip_adapter_scale=0.5, **kwargs):
        """
        Generate an image from a text prompt, optionally with a reference image
        
        Args:
            prompt (str): Text description of the logo to generate
            use_lora (bool): Whether to use LoRA weights
            lora_filename (str): Specific LoRA file to use (if use_lora=True)
            reference_image (PIL.Image or str): Reference image for IP-Adapter
            ip_adapter_scale (float): Strength of IP-Adapter influence (0.0-1.0)
            **kwargs: Additional generation parameters
            
        Returns:
            PIL.Image: Generated image
        """
        # Ensure correct model is loaded
        if use_lora:
            # Check if we need to load a different LoRA or load for first time
            if not self.lora_loaded or (lora_filename and self.current_lora != lora_filename):
                self.load_lora(lora_filename)
        elif self.lora_loaded:
            self.unload_lora()
        elif not self.base_model_loaded:
            self.load_base_model()
        
        # Load IP-Adapter if reference image provided and not loaded
        if reference_image is not None and not self.ip_adapter_loaded:
            self.load_ip_adapter()
        
        # Process reference image if provided
        if reference_image is not None:
            if isinstance(reference_image, str):
                # Load from path
                reference_image = Image.open(reference_image).convert("RGB")
            elif not isinstance(reference_image, Image.Image):
                raise ValueError("reference_image must be a PIL Image or file path")
        
        # Merge default params with custom ones
        gen_params = config.DEFAULT_GENERATION_PARAMS.copy()
        gen_params.update(kwargs)
        
        try:
            mode = []
            if use_lora:
                mode.append("LoRA")
            if reference_image is not None:
                mode.append(f"IP-Adapter (scale: {ip_adapter_scale})")
            mode_str = " + ".join(mode) if mode else "base model"
            
            print(f"Generating image with {mode_str}...")
            print(f"Prompt: {prompt}")
            
            # Prepare generation arguments
            gen_args = {
                "prompt": prompt,
                **gen_params
            }
            
            # Add IP-Adapter arguments if reference image provided
            if reference_image is not None and self.ip_adapter_loaded:
                gen_args["ip_adapter_image"] = reference_image
                gen_args["ip_adapter_image_embeds"] = None
                # Set IP-Adapter scale
                self.pipeline.set_ip_adapter_scale(ip_adapter_scale)
            
            # Add LoRA scale if using LoRA
            if use_lora:
                gen_args["cross_attention_kwargs"] = {"scale": config.LORA_SCALE}
            
            # Generate image
            with torch.inference_mode():
                result = self.pipeline(**gen_args)
            
            image = result.images[0]
            print("✓ Image generated successfully")
            return image
            
        except Exception as e:
            print(f"Error generating image: {e}")
            raise
    
    def get_model_info(self):
        """Get information about the current model state"""
        return {
            "base_model_loaded": self.base_model_loaded,
            "lora_loaded": self.lora_loaded,
            "current_lora": self.current_lora,
            "available_loras": self.get_available_loras(),
            "ip_adapter_loaded": self.ip_adapter_loaded,
            "device": self.device,
            "model_id": config.BASE_MODEL_ID if self.base_model_loaded else None
        }
