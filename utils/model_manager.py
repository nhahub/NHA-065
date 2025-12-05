"""
Model Manager for Zypher AI Logo Generator
Handles loading and managing Flux Schnell model with optional LoRA and FLUX Redux
"""
import torch
from diffusers import FluxPipeline, FluxPriorReduxPipeline
from PIL import Image
import os
from dotenv import load_dotenv
import config

# Load environment variables
load_dotenv()

class ModelManager:
    """Manages the Flux Schnell model, LoRA weights, and FLUX Redux"""
    
    def __init__(self):
        self.pipeline = None
        self.redux_pipeline = None
        self.device = config.GPU_DEVICE if config.USE_GPU and torch.cuda.is_available() else "cpu"
        self.lora_loaded = False
        self.current_lora = None  # Track which LoRA is currently loaded
        self.base_model_loaded = False
        self.redux_loaded = False
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
                dtype=torch.bfloat16 if self.device != "cpu" else torch.float32,
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
            
            # Set LoRA scale/strength for Flux models
            # In newer diffusers, we can use set_adapters or fuse the LoRA
            try:
                # Try to set the adapter scale
                self.pipeline.set_adapters(["default"], adapter_weights=[config.LORA_SCALE])
            except:
                # If that doesn't work, the scale might be applied automatically
                print(f"Note: Using default LoRA scale (scale set during generation)")
            
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
    
    def load_redux(self):
        """Load FLUX Redux for image-to-image conditioning"""
        if not self.base_model_loaded:
            self.load_base_model()
        
        if self.redux_loaded:
            print("FLUX Redux already loaded")
            return
        
        try:
            print("Loading FLUX Redux adapter...")
            # Load FLUX Redux - the official image conditioning adapter for FLUX models
            self.redux_pipeline = FluxPriorReduxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-Redux-dev",
                torch_dtype=torch.bfloat16 if self.device != "cpu" else torch.float32,
                token=self.hf_token if self.hf_token and self.hf_token != "your_huggingface_token_here" else None
            )
            self.redux_pipeline.to(self.device)
            
            self.redux_loaded = True
            print("✓ FLUX Redux loaded successfully")
        except Exception as e:
            print(f"Error loading FLUX Redux: {e}")
            print("Continuing without Redux support...")
            self.redux_loaded = False
            raise
    
    def generate_image(self, prompt, use_lora=False, lora_filename=None, reference_image=None, ip_adapter_scale=0.5, **kwargs):
        """
        Generate an image from a text prompt, optionally with a reference image using FLUX Redux
        
        FLUX Redux combines both text prompt and reference image:
        - The text prompt describes what you want to create
        - The reference image guides the style, composition, and visual characteristics
        - ip_adapter_scale controls how much influence the reference has (0.0=text only, 1.0=strong reference)
        
        Args:
            prompt (str): Text description of the logo to generate
            use_lora (bool): Whether to use LoRA weights
            lora_filename (str): Specific LoRA file to use (if use_lora=True)
            reference_image (PIL.Image or str): Reference image for FLUX Redux
            ip_adapter_scale (float): Strength of Redux influence (0.0-1.0, default 0.5)
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
        
        # Load FLUX Redux if reference image provided and not loaded
        if reference_image is not None and not self.redux_loaded:
            try:
                self.load_redux()
            except Exception as e:
                print(f"Warning: Could not load FLUX Redux: {e}")
                print("Continuing with text-only generation...")
                reference_image = None
        
        # Process reference image if provided
        redux_output = None
        if reference_image is not None:
            if isinstance(reference_image, str):
                # Load from path
                reference_image = Image.open(reference_image).convert("RGB")
            elif not isinstance(reference_image, Image.Image):
                raise ValueError("reference_image must be a PIL Image or file path")
            
            # Generate Redux embeddings from reference image
            if self.redux_loaded:
                try:
                    print("Processing reference image with FLUX Redux...")
                    print(f"Redux influence scale: {ip_adapter_scale}")
                    with torch.inference_mode():
                        # FLUX Redux processes the reference image into embeddings
                        redux_output = self.redux_pipeline(reference_image)
                    print("✓ Reference image processed")
                except Exception as e:
                    print(f"Warning: Error processing reference image: {e}")
                    redux_output = None
        
        # Merge default params with custom ones
        gen_params = config.DEFAULT_GENERATION_PARAMS.copy()
        
        # Map 'num_steps' to 'num_inference_steps' if provided
        if 'num_steps' in kwargs:
            kwargs['num_inference_steps'] = kwargs.pop('num_steps')
        
        # Remove custom parameters that shouldn't be passed to FluxPipeline
        # These are handled separately above
        custom_params = ['use_lora', 'lora_filename', 'use_ip_adapter', 'chat_entry_id']
        for param in custom_params:
            kwargs.pop(param, None)
        
        gen_params.update(kwargs)
        
        try:
            mode = []
            if use_lora:
                mode.append("LoRA")
            if redux_output is not None:
                mode.append(f"FLUX Redux (scale: {ip_adapter_scale})")
            mode_str = " + ".join(mode) if mode else "base model"
            
            print(f"Generating image with {mode_str}...")
            print(f"Prompt: {prompt}")
            
            # Prepare generation arguments
            # ALWAYS include the text prompt - it describes what to create
            gen_args = {
                "prompt": prompt,
                **gen_params
            }
            
            # Add Redux outputs if reference image was processed
            if redux_output is not None:
                # FLUX Redux provides image embeddings that guide the generation
                # We use BOTH the text prompt (what to create) and embeddings (style/reference)
                
                # Redux output is a namespace/dict-like object, not a regular dict
                # Extract the pooled embeddings for visual guidance
                try:
                    # Try different ways to access Redux embeddings
                    if hasattr(redux_output, 'pooled_image_embeds'):
                        gen_args["pooled_projections"] = redux_output.pooled_image_embeds
                        print(f"✓ Using Redux pooled_image_embeds with text prompt (influence: {ip_adapter_scale})")
                    elif hasattr(redux_output, 'image_embeds'):
                        gen_args["pooled_projections"] = redux_output.image_embeds
                        print(f"✓ Using Redux image_embeds with text prompt (influence: {ip_adapter_scale})")
                    elif isinstance(redux_output, dict):
                        # If it's a dict, try to get embeddings
                        if 'pooled_image_embeds' in redux_output:
                            gen_args["pooled_projections"] = redux_output["pooled_image_embeds"]
                            print(f"✓ Using Redux visual guidance (dict) with text prompt (influence: {ip_adapter_scale})")
                        elif 'image_embeds' in redux_output:
                            gen_args["pooled_projections"] = redux_output["image_embeds"]
                            print(f"✓ Using Redux visual guidance (dict) with text prompt (influence: {ip_adapter_scale})")
                    else:
                        print(f"⚠️ Redux output type: {type(redux_output)}")
                        print(f"⚠️ Redux output attributes: {dir(redux_output)}")
                        print("⚠️ Redux output format unexpected, using text prompt only")
                except Exception as e:
                    print(f"⚠️ Error extracting Redux embeddings: {e}")
                    print("⚠️ Continuing with text prompt only")
                
                # Adjust guidance scale based on redux influence
                # Higher ip_adapter_scale means more influence from reference image
                base_guidance = gen_params.get("guidance_scale", 3.5)
                gen_args["guidance_scale"] = base_guidance * (1.0 + ip_adapter_scale)
                print(f"Adjusted guidance_scale: {gen_args['guidance_scale']:.2f} (base: {base_guidance}, scale: {ip_adapter_scale})")
            
            # Note: For Flux models, LoRA scale is set during loading, not during generation
            
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
            "redux_loaded": self.redux_loaded,
            "ip_adapter_loaded": self.redux_loaded,  # Alias for backward compatibility
            "device": self.device,
            "model_id": config.BASE_MODEL_ID if self.base_model_loaded else None
        }
