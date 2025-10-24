"""
Zypher AI Logo Generator - Main Application
A Gradio-based web interface for generating logos using Flux Schnell with optional LoRA
"""
import gradio as gr
import os
from datetime import datetime
from PIL import Image
import sys

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from utils.model_manager import ModelManager
from utils.chat_history import ChatHistoryManager


class ZypherApp:
    """Main application class for Zypher AI Logo Generator"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.chat_history = ChatHistoryManager()
        print(f"🚀 Initializing {config.PROJECT_NAME} v{config.VERSION}")
        
    def generate_logo(self, prompt, use_lora, num_steps, width, height, history):
        """
        Generate a logo from a text prompt
        
        Args:
            prompt (str): Text description of the logo
            use_lora (bool): Whether to use LoRA model
            num_steps (int): Number of inference steps
            width (int): Image width
            height (int): Image height
            history (list): Current chat history
            
        Returns:
            tuple: (image, updated_history, status_message)
        """
        if not prompt or prompt.strip() == "":
            return None, history, "⚠️ Please enter a prompt"
        
        try:
            # Update status
            status = f"🎨 Generating logo with {'LoRA' if use_lora else 'Base Model'}..."
            
            # Generate image
            image = self.model_manager.generate_image(
                prompt=prompt,
                use_lora=use_lora,
                num_inference_steps=num_steps,
                width=width,
                height=height
            )
            
            # Save image
            if config.SAVE_GENERATED_IMAGES:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"logo_{timestamp}.{config.IMAGE_FORMAT.lower()}"
                image_path = os.path.join(config.OUTPUTS_DIR, filename)
                image.save(image_path, format=config.IMAGE_FORMAT)
            else:
                image_path = "not_saved"
            
            # Add to chat history
            self.chat_history.add_entry(prompt, image_path, use_lora)
            
            # Update chat display
            model_type = "🔮 LoRA Model" if use_lora else "⚡ Base Model"
            user_message = prompt
            assistant_message = f"Generated with {model_type}"
            history.append([user_message, assistant_message])
            
            success_msg = f"✅ Logo generated successfully!\nSaved to: {image_path}"
            return image, history, success_msg
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            return None, history, error_msg
    
    def load_history_display(self):
        """Load chat history for display"""
        return self.chat_history.format_for_display()
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_history.clear_history()
        return [], "🗑️ Chat history cleared"
    
    def get_model_status(self):
        """Get current model status"""
        info = self.model_manager.get_model_info()
        status_lines = [
            f"**Model Status:**",
            f"• Base Model: {'✓ Loaded' if info['base_model_loaded'] else '✗ Not loaded'}",
            f"• LoRA: {'✓ Loaded' if info['lora_loaded'] else '✗ Not loaded'}",
            f"• Device: {info['device']}",
            f"• Model ID: {info['model_id'] or 'None'}"
        ]
        return "\n".join(status_lines)
    
    def create_interface(self):
        """Create and configure the Gradio interface"""
        
        # Custom CSS for better styling
        custom_css = """
        .logo-container {
            text-align: center;
            padding: 20px;
        }
        .generate-btn {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        .status-box {
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
        }
        """
        
        with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title=config.PROJECT_NAME) as interface:
            
            # Header
            gr.Markdown(
                f"""
                # 🎨 {config.PROJECT_NAME}
                ### Powered by Flux Schnell - Generate stunning logos with AI
                """
            )
            
            with gr.Row():
                # Left column - Controls
                with gr.Column(scale=1):
                    gr.Markdown("### 💬 Prompt")
                    prompt_input = gr.Textbox(
                        label="Describe your logo",
                        placeholder="e.g., A modern tech company logo with blue and silver colors, minimalist design",
                        lines=3
                    )
                    
                    gr.Markdown("### ⚙️ Settings")
                    
                    use_lora = gr.Checkbox(
                        label="Use LoRA Model",
                        value=False,
                        info="Enable your custom trained LoRA weights"
                    )
                    
                    with gr.Accordion("Advanced Settings", open=False):
                        num_steps = gr.Slider(
                            minimum=1,
                            maximum=8,
                            value=config.DEFAULT_GENERATION_PARAMS["num_inference_steps"],
                            step=1,
                            label="Inference Steps",
                            info="Flux Schnell works best with 1-4 steps"
                        )
                        
                        with gr.Row():
                            width = gr.Slider(
                                minimum=512,
                                maximum=1536,
                                value=config.DEFAULT_GENERATION_PARAMS["width"],
                                step=64,
                                label="Width"
                            )
                            height = gr.Slider(
                                minimum=512,
                                maximum=1536,
                                value=config.DEFAULT_GENERATION_PARAMS["height"],
                                step=64,
                                label="Height"
                            )
                    
                    generate_btn = gr.Button(
                        "🚀 Generate Logo",
                        variant="primary",
                        elem_classes="generate-btn"
                    )
                    
                    status_output = gr.Textbox(
                        label="Status",
                        lines=3,
                        interactive=False,
                        elem_classes="status-box"
                    )
                    
                    with gr.Row():
                        clear_btn = gr.Button("🗑️ Clear History", size="sm")
                        model_status_btn = gr.Button("📊 Model Status", size="sm")
                
                # Middle column - Generated Image
                with gr.Column(scale=1):
                    gr.Markdown("### 🖼️ Generated Logo")
                    output_image = gr.Image(
                        label="Your Logo",
                        type="pil",
                        height=500
                    )
                
                # Right column - Chat History
                with gr.Column(scale=1):
                    gr.Markdown("### 📜 Chat History")
                    chatbot = gr.Chatbot(
                        label="Generation History",
                        height=500,
                        value=self.load_history_display()
                    )
            
            # Footer
            gr.Markdown(
                """
                ---
                **Tips:**
                - Flux Schnell is optimized for fast generation (1-4 steps)
                - Toggle LoRA to use your custom trained model
                - All generated images are saved to the `outputs` folder
                - Chat history is automatically saved
                """
            )
            
            # Event handlers
            generate_btn.click(
                fn=self.generate_logo,
                inputs=[prompt_input, use_lora, num_steps, width, height, chatbot],
                outputs=[output_image, chatbot, status_output]
            )
            
            clear_btn.click(
                fn=self.clear_chat,
                outputs=[chatbot, status_output]
            )
            
            model_status_btn.click(
                fn=self.get_model_status,
                outputs=status_output
            )
        
        return interface
    
    def launch(self):
        """Launch the Gradio application"""
        interface = self.create_interface()
        
        print(f"\n{'='*60}")
        print(f"🎨 {config.PROJECT_NAME} v{config.VERSION}")
        print(f"{'='*60}\n")
        
        interface.launch(
            share=config.SHARE_LINK,
            server_name=config.SERVER_NAME,
            server_port=config.SERVER_PORT
        )


if __name__ == "__main__":
    app = ZypherApp()
    app.launch()
