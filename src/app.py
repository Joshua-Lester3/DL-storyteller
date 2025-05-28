from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Input, Static, LoadingIndicator, Footer
from textual.binding import Binding
from textual.screen import Screen
from chatbot import ChatBot
import asyncio


class SelectionScreen(Screen[int]):
    """
    A screen that presents a list of options using ListView
    and updates the display based on the selected option.
    """
    def compose(self) -> ComposeResult:
        logo = r"""
  __                   __                   .___                    __
_/  |_  ____ ___  ____/  |_     _____     __| _/__  __ ____   _____/  |_ __ _________   ____
\   __\/ __ \\  \/  /\   __\    \__  \   / __ |\  \/ // __ \ /    \   __\  |  \_  __ \_/ __ \
 |  | \  ___/ >    <  |  |       / __ \_/ /_/ | \   /\  ___/|   |  \  | |  |  /|  | \/\  ___/
 |__|  \___  >__/\_ \ |__|      (____  /\____ |  \_/  \___  >___|  /__| |____/ |__|    \___  >
           \/      \/                \/      \/           \/     \/                        \/

"""
        yield Static(logo)
        yield Static("Select an option to begin:", id="prompt_selection")
        yield ListView(
            ListItem(Static("Solo explorer crash landed on mysterious floating island in the sky."), id="option0"),
            ListItem(Static("You're a child in an orphanage. But something strange is going on, and something is wrong with this place."), id="option1"),
            ListItem(Static("You're chained in a cave dungeon. What will you do?!"), id="option2"),
            id="options_list",
        )
        yield Static("", id="result_selection")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        result_widget = self.query_one("#result_selection", Static)
        choice_id = event.item.id
        messages = {
            "option1": "You chose Option 1!",
            "option2": "You chose Option 2!",
            "option3": "You chose Option 3!",
        }
        result_widget.update(messages.get(choice_id, f"Selected: {choice_id}"))
        # After selection, return to main application view
        self.dismiss(int(choice_id[-1]))



class Pager(Static):
    """
    A simple widget to display text pages.
    """
    can_focus = True
    def show_page(self, content: str) -> None:
        self.update(content)

class PromptDisplay(Static):
    def show_prompt(self, prompt: str) -> None:
        self.update(f"[Bold]User: [/] {prompt}")

class TextPagerApp(App[None]):
    BINDINGS = [
        Binding("left", "prev_page", "Previous Page"),
        Binding("right", "next_page", "Next Page"),
        Binding("enter", "focus_input", "Focus Input"),
        Binding("escape", "unfocus_input", "Unfocus Input")
    ]

    CSS = """
    Screen {
        layout: vertical;
        align: center middle;
    }
    Pager {
        height: 1fr;
        width: 100%;
        padding: 1;
        border: solid green;
    }
    PromptDisplay {
        height: 3;
        width: 100%;
        padding: 1;
        border: solid yellow;
    }
    Input {
        width: 100%;
        border: solid blue;
    }
    LoadingIndicator {
        dock: bottom;
        padding: 1;
    }
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(**kwargs)
        self.pages = [{"response" : "", "prompt": ""}]
        self.current_index = 0
        self.chatbot = chatbot

    def compose(self) -> ComposeResult:
        page = self.pages[self.current_index]
        if isinstance(page, dict):
            resp = page.get("response", "")
        else:
            resp = page

        yield Pager(resp, id="pager")
        yield PromptDisplay("", id="prompt_display")
        yield Input(placeholder="Type and press Enter to add a page...", id="cmd_input")
        yield LoadingIndicator(id="loading")
        yield Footer()

    async def on_ready(self) -> None:
        def check_result(choice: int | None) -> None:
            if choice is not None:
                self.choice = choice
                with open('/home/azureuser/DL-storyteller/docs/stories.txt', 'r', encoding='utf-8') as f:
                    text = f.read()
                    stories = text.split('---')
                prompt = stories[self.choice]
                resp = await self.helper(prompt)
                page = self.pages[self.current_index]
                page["response"] = resp

        self.push_screen(SelectionScreen(), callback=check_result)

    def on_mount(self) -> None:
        self.query_one(PromptDisplay).display = False
        self.query_one(LoadingIndicator).display = False
        # Ensure initial focus and correct widget visibility
        self.update_view()
        self.set_focus(self.query_one(Input))

    def update_view(self) -> None:
        page = self.pages[self.current_index]
        if isinstance(page, dict):
            resp = page.get("response", "")
            prompt = page.get("prompt")
        else:
            resp = page
            prompt = None
        self.query_one(Pager).show_page(resp)
        prompt_widget = self.query_one(PromptDisplay)
        input_widget = self.query_one(Input)
        if prompt:
            prompt_widget.display = True
            prompt_widget.show_prompt(prompt)
            input_widget.display = False
        else:
            prompt_widget.display = False
            input_widget.display = True

    def action_next_page(self) -> None:
        if len(self.pages) > 1:
            self.current_index = (self.current_index + 1) % len(self.pages)
            self.update_view()

    def action_prev_page(self) -> None:
        if len(self.pages) > 1:
            self.current_index = (self.current_index - 1) % len(self.pages)
            self.update_view()

    def action_focus_input(self) -> None:
        self.set_focus(self.query_one(Input))

    def action_unfocus_input(self) -> None:
        self.set_focus(self.query_one(Pager))

    async def helper(self, prompt: str):
        if not prompt:
            return

        # Show spinner while waiting
        spinner = self.query_one(LoadingIndicator)
        spinner.display = True
        self.refresh(layout=True)

        # Run blocking LLM call in thread
        try:
            _, response = await asyncio.to_thread(self.chatbot.prompt, prompt)
        except Exception as err:
            response = f"[red]Error:[/] {err}"
        finally:
            spinner.display = False
        spinner.display = False
        last_index = len(self.pages) - 1
        self.pages[last_index]["prompt"] = prompt
        self.pages.append({"response": response, "prompt": None})
        self.current_index = len(self.pages) - 1

        self.update_view()
        return response



    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Add input text as a new page and display it
        prompt = event.value.strip()
        # Hide spinner and update pages
        event.input.value = ""

        response = await self.helper(prompt)
        # Return focus to pager so arrow keys work

if __name__ == "__main__":
    chatbot = ChatBot()
    # Initialize with only the first page
    app = TextPagerApp(chatbot=chatbot)
    app.run()
