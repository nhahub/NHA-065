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
            return None, history, "⚠️ Please enter a prompt to generate your logo"
        
        try:
            # Update status with detailed info
            model_name = "LoRA Fine-tuned" if use_lora else "Base Flux Schnell"
            status = f"""🎨 **Generating your logo...**
            
• Model: {model_name}
• Steps: {num_steps}
• Resolution: {width}×{height}px
• Processing..."""
            
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
            
            # Update chat display with rich formatting
            model_type = "🔮 LoRA Fine-tuned Model" if use_lora else "⚡ Base Flux Schnell"
            user_message = prompt
            assistant_message = f"""Generated with **{model_type}**

✨ **Settings Used:**
• Inference steps: {num_steps}
• Dimensions: {width}×{height}px
• Saved: `{os.path.basename(image_path)}`"""
            
            history.append([user_message, assistant_message])
            
            # Success message with details
            success_msg = f"""✅ **Generation Complete!**

📁 Saved to: `{image_path}`
🎨 Model: {model_name}
⚡ Steps: {num_steps} | 📐 Size: {width}×{height}px
⏱️ Generated at: {datetime.now().strftime("%H:%M:%S")}"""
            
            return image, history, success_msg
            
        except Exception as e:
            error_msg = f"""❌ **Generation Failed**

**Error:** {str(e)}

💡 **Troubleshooting:**
• Check if the model is loaded correctly
• Ensure sufficient memory is available
• Try reducing image dimensions or steps"""
            return None, history, error_msg
    
    def load_history_display(self):
        """Load chat history for display"""
        return self.chat_history.format_for_display()
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_history.clear_history()
        return [], "🗑️ **Chat history cleared successfully**\n\nReady for new generations!"
    
    def get_model_status(self):
        """Get current model status"""
        info = self.model_manager.get_model_info()
        
        status_lines = [
            "📊 **Model Status Report**",
            "",
            f"**Base Model:** {'✅ Loaded' if info['base_model_loaded'] else '❌ Not loaded'}",
            f"**LoRA Model:** {'✅ Loaded' if info['lora_loaded'] else '⚠️ Not loaded'}",
            "",
            f"**Device:** `{info['device']}`",
            f"**Model ID:** `{info['model_id'] or 'None'}`",
            "",
            f"**Status:** {'🟢 Ready to generate' if info['base_model_loaded'] else '🔴 Model not ready'}"
        ]
        return "\n".join(status_lines)
    
    def create_interface(self):
        """Create and configure the Gradio interface"""
        
        # Custom CSS for Claude-inspired modern design
        custom_css = """
        /* Global Styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main Container */
        .gradio-container {
            max-width: 1400px !important;
            margin: 0 auto !important;
        }
        
        /* Header Styles */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
            text-align: center;
        }
        
        .header-container h1 {
            color: white;
            font-weight: 700;
            font-size: 2.5rem;
            margin: 0;
            letter-spacing: -0.02em;
        }
        
        .header-container p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            font-weight: 400;
        }
        
        /* Chat Interface Styles */
        .chat-container {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
        }
        
        /* Input Area */
        .prompt-container {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .prompt-container:focus-within {
            border-color: #667eea;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
        }
        
        textarea {
            border: none !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
        }
        
        textarea:focus {
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Button Styles */
        .generate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            padding: 0.875rem 2rem !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3) !important;
            text-transform: none !important;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4) !important;
        }
        
        .generate-btn:active {
            transform: translateY(0) !important;
        }
        
        /* Secondary Buttons */
        button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        /* Settings Panel */
        .settings-panel {
            background: rgba(102, 126, 234, 0.03);
            border-radius: 12px;
            padding: 1.25rem;
            border: 1px solid rgba(102, 126, 234, 0.1);
            margin-top: 1rem;
        }
        
        /* Accordion Styles */
        .accordion {
            background: transparent !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 10px !important;
            margin-top: 1rem !important;
        }
        
        /* Slider Styles */
        input[type="range"] {
            accent-color: #667eea !important;
        }
        
        /* Image Output */
        .image-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            background: white;
            padding: 1rem;
        }
        
        /* Status Box */
        .status-box {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 10px;
            padding: 1rem;
            font-size: 14px;
            line-height: 1.6;
            margin-top: 1rem;
        }
        
        /* Chatbot Styles */
        .chatbot-container {
            border-radius: 12px !important;
            border: 1px solid rgba(102, 126, 234, 0.15) !important;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08) !important;
        }
        
        /* Section Headers */
        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Footer */
        .footer-tips {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
            border: 1px solid rgba(102, 126, 234, 0.15);
        }
        
        .footer-tips ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        
        .footer-tips li {
            margin: 0.5rem 0;
            line-height: 1.6;
            color: #4b5563;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .card, .chat-container {
            animation: fadeIn 0.4s ease-out;
        }
        
        /* Dark mode support */
        .dark .card {
            background: rgba(31, 41, 55, 0.8);
            border-color: rgba(102, 126, 234, 0.2);
        }
        
        .dark .section-header {
            color: #f9fafb;
        }
        
        /* Checkbox and Radio Styles */
        input[type="checkbox"] {
            accent-color: #667eea !important;
            width: 18px;
            height: 18px;
        }
        
        /* Label Styles */
        label {
            font-weight: 500 !important;
            color: #374151 !important;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header-container h1 {
                font-size: 1.875rem;
            }
            
            .gradio-container {
                padding: 1rem !important;
            }
        }
        """
        
        # Create custom theme based on Soft theme
        custom_theme = gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="purple",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
        ).set(
            body_background_fill="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            body_background_fill_dark="linear-gradient(135deg, #1f2937 0%, #111827 100%)",
            button_primary_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            button_primary_background_fill_hover="linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
            slider_color="#667eea",
        )
        
        with gr.Blocks(theme=custom_theme, css=custom_css, title=config.PROJECT_NAME) as interface:
            
            # Header with modern gradient design
            with gr.Row(elem_classes="header-container"):
                gr.Markdown(
                    f"""
                    <div style="text-align: center;">
                        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🎨 {config.PROJECT_NAME}</h1>
                        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">Powered by Flux Schnell • AI-Driven Logo Generation</p>
                    </div>
                    """
                )
            
            # Main content area - Claude-inspired layout
            with gr.Row():
                # Left sidebar - Controls (30%)
                with gr.Column(scale=3, min_width=320):
                    with gr.Group(elem_classes="card"):
                        gr.HTML('<div class="section-header">💬 Prompt</div>')
                        prompt_input = gr.Textbox(
                            label="",
                            placeholder="Describe your logo in detail...\n\ne.g., A modern tech startup logo featuring a geometric hexagon symbol, gradient from deep blue to cyan, clean sans-serif typography, minimalist and professional design",
                            lines=5,
                            show_label=False,
                            elem_classes="prompt-container"
                        )
                        
                        generate_btn = gr.Button(
                            "✨ Generate Logo",
                            variant="primary",
                            size="lg",
                            elem_classes="generate-btn"
                        )
                    
                    with gr.Group(elem_classes="card settings-panel"):
                        gr.HTML('<div class="section-header">⚙️ Model Settings</div>')
                        
                        use_lora = gr.Checkbox(
                            label="🔮 Use LoRA Fine-tuned Model",
                            value=False,
                            info="Enable your custom trained weights for specialized styles"
                        )
                        
                        with gr.Accordion("🎛️ Advanced Parameters", open=False, elem_classes="accordion"):
                            num_steps = gr.Slider(
                                minimum=1,
                                maximum=8,
                                value=config.DEFAULT_GENERATION_PARAMS["num_inference_steps"],
                                step=1,
                                label="⚡ Inference Steps",
                                info="Flux Schnell is optimized for 1-4 steps (faster = less detailed)"
                            )
                            
                            gr.Markdown("**📐 Image Dimensions**")
                            with gr.Row():
                                width = gr.Slider(
                                    minimum=512,
                                    maximum=1536,
                                    value=config.DEFAULT_GENERATION_PARAMS["width"],
                                    step=64,
                                    label="Width (px)"
                                )
                                height = gr.Slider(
                                    minimum=512,
                                    maximum=1536,
                                    value=config.DEFAULT_GENERATION_PARAMS["height"],
                                    step=64,
                                    label="Height (px)"
                                )
                    
                    # Status and controls
                    status_output = gr.Textbox(
                        label="",
                        lines=3,
                        interactive=False,
                        show_label=False,
                        elem_classes="status-box",
                        placeholder="Ready to generate..."
                    )
                    
                    with gr.Row():
                        model_status_btn = gr.Button("� Model Info", size="sm", variant="secondary")
                        clear_btn = gr.Button("�️ Clear History", size="sm", variant="secondary")
                
                # Center - Generated Image (40%)
                with gr.Column(scale=4, min_width=400):
                    with gr.Group(elem_classes="card"):
                        gr.HTML('<div class="section-header">🖼️ Generated Output</div>')
                        output_image = gr.Image(
                            label="",
                            type="pil",
                            height=600,
                            show_label=False,
                            elem_classes="image-container",
                            show_download_button=True
                        )
                
                # Right sidebar - Chat History (30%)
                with gr.Column(scale=3, min_width=320):
                    with gr.Group(elem_classes="card"):
                        gr.HTML('<div class="section-header">📜 Generation History</div>')
                        chatbot = gr.Chatbot(
                            label="",
                            height=750,
                            show_label=False,
                            value=self.load_history_display(),
                            elem_classes="chatbot-container",
                            type="tuples",
                            avatar_images=(
                                "https://api.dicebear.com/7.x/avataaars/svg?seed=user",
                                "https://api.dicebear.com/7.x/bottts/svg?seed=ai"
                            )
                        )
            
            # Footer with tips
            with gr.Group(elem_classes="footer-tips"):
                gr.Markdown(
                    """
                    ### 💡 Pro Tips
                    
                    - **Quality Prompts**: Be specific about style, colors, symbols, and mood for best results
                    - **Fast Generation**: Flux Schnell excels at 1-4 inference steps (vs. 50+ for traditional models)
                    - **LoRA Models**: Toggle the LoRA option to apply your custom trained style
                    - **Auto-Save**: All generated images are automatically saved to `/outputs` directory
                    - **Persistent History**: Your generation history is saved and restored on restart
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
