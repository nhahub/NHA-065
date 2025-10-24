"""
Model Manager for Zypher AI Logo Generator
Handles loading and managing Flux Schnell model with optional LoRA
"""
import torch
from diffusers import FluxPipeline
import os
import config


class ModelManager:
    """Manages the Flux Schnell model and LoRA weights"""
    
    def __init__(self):
        self.pipeline = None
        self.device = config.GPU_DEVICE if config.USE_GPU and torch.cuda.is_available() else "cpu"
        self.lora_loaded = False
        self.base_model_loaded = False
        
    def load_base_model(self):
        """Load the base Flux Schnell model"""
        if self.base_model_loaded and self.pipeline is not None:
            print("Base model already loaded")
            return
            
        try:
            print(f"Loading Flux Schnell model on {self.device}...")
            self.pipeline = FluxPipeline.from_pretrained(
                config.BASE_MODEL_ID,
                torch_dtype=torch.bfloat16 if self.device != "cpu" else torch.float32
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
            raise
    
    def load_lora(self):
        """Load LoRA weights on top of the base model"""
        if not self.base_model_loaded:
            self.load_base_model()
        
        lora_path = os.path.join(config.LORA_MODEL_PATH, config.LORA_WEIGHTS_FILE)
        
        if not os.path.exists(lora_path):
            raise FileNotFoundError(
                f"LoRA weights not found at {lora_path}. "
                f"Please place your LoRA weights in the models/lora folder."
            )
        
        try:
            print("Loading LoRA weights...")
            # Unload any existing LoRA first
            if self.lora_loaded:
                self.pipeline.unload_lora_weights()
            
            # Load new LoRA weights
            self.pipeline.load_lora_weights(config.LORA_MODEL_PATH)
            self.lora_loaded = True
            print(f"✓ LoRA weights loaded successfully (scale: {config.LORA_SCALE})")
        except Exception as e:
            print(f"Error loading LoRA: {e}")
            raise
    
    def unload_lora(self):
        """Unload LoRA weights to use base model only"""
        if self.lora_loaded and self.pipeline is not None:
            try:
                print("Unloading LoRA weights...")
                self.pipeline.unload_lora_weights()
                self.lora_loaded = False
                print("✓ LoRA weights unloaded, using base model")
            except Exception as e:
                print(f"Error unloading LoRA: {e}")
    
    def generate_image(self, prompt, use_lora=False, **kwargs):
        """
        Generate an image from a text prompt
        
        Args:
            prompt (str): Text description of the logo to generate
            use_lora (bool): Whether to use LoRA weights
            **kwargs: Additional generation parameters
            
        Returns:
            PIL.Image: Generated image
        """
        # Ensure correct model is loaded
        if use_lora and not self.lora_loaded:
            self.load_lora()
        elif not use_lora and self.lora_loaded:
            self.unload_lora()
        elif not self.base_model_loaded:
            self.load_base_model()
        
        # Merge default params with custom ones
        gen_params = config.DEFAULT_GENERATION_PARAMS.copy()
        gen_params.update(kwargs)
        
        try:
            print(f"Generating image with {'LoRA' if use_lora else 'base model'}...")
            print(f"Prompt: {prompt}")
            
            # Generate image
            with torch.inference_mode():
                result = self.pipeline(
                    prompt=prompt,
                    **gen_params,
                    cross_attention_kwargs={"scale": config.LORA_SCALE} if use_lora else None
                )
            
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
            "device": self.device,
            "model_id": config.BASE_MODEL_ID if self.base_model_loaded else None
        }
