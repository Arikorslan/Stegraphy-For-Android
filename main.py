import os
import threading
from pathlib import Path
from sys import platform

from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.widget import MDWidget
from plyer import filechooser, notification

try:
    from kivymd.uix.button import MDRaisedButton as LegacyDialogButton
except Exception:
    LegacyDialogButton = None

try:
    from kivymd.uix.button import MDButton, MDButtonText
except Exception:
    MDButton = None
    MDButtonText = None

try:
    from kivymd.uix.dialog import (
        MDDialogHeadlineText,
        MDDialogSupportingText,
        MDDialogButtonContainer,
        MDDialogContentContainer,
    )
except Exception:
    MDDialogHeadlineText = None
    MDDialogSupportingText = None
    MDDialogButtonContainer = None
    MDDialogContentContainer = None

from least_significant_bit import EncodeMessage
from update import APP_VERSION, GITHUB_REPOSITORY_URL, check_for_update

try:
    if platform == "android":
        from kivymd.toast import toast as _android_toast
    else:
        _android_toast = None
except Exception:
    _android_toast = None


def app_toast(message):
    if _android_toast:
        _android_toast(message)
    else:
        notification.notify(title="Stegnography", message=str(message))


def make_dialog_button(text, callback):
    # KivyMD <2.0 used MDRaisedButton/MDFlatButton, KivyMD 2.0 uses MDButton + MDButtonText.
    if LegacyDialogButton is not None:
        return LegacyDialogButton(text=text, on_release=callback)

    if MDButton is not None and MDButtonText is not None:
        return MDButton(
            MDButtonText(text=text),
            style="text",
            on_release=callback,
        )

    raise ImportError("No compatible KivyMD dialog button class found for this version.")

primary_ext_storage = ""
app_storage = ""
os.environ['KIVY_IMAGE'] = "pil,sdl2"

try:
    from jnius import autoclass
    from plyer.platforms.android import activity
    from android.storage import app_storage_path, primary_external_storage_path
    from android.permissions import Permission, request_permissions
    
    primary_ext_storage = primary_external_storage_path()#os.path.join(os.getenv('EXTERNAL_STORAGE'),'Downloads')#primary_external_storage_path()
    app_storage = app_storage_path()


except:
    primary_ext_storage = "/"
    app_storage = str(Path.home())
    pass


# __version__ = '0.1.2023'
#Window.size = (300,600)
#<div>Icons made by <a href="https://www.flaticon.com/authors/tomas-knop" title="Tomas Knop">Tomas Knop</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><div>Icons made by <a href="https://www.flaticon.com/authors/itim2101" title="itim2101">itim2101</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><div>Icons made by <a href="https://www.flaticon.com/authors/rizki-ahmad-fauzi" title="Rizki Ahmad Fauzi">Rizki Ahmad Fauzi</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><div>Icons made by <a href="https://www.flaticon.com/authors/omoonstd" title="O.moonstd">O.moonstd</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><div>Icons made by <a href="https://www.flaticon.com/authors/ehtisham-abid" title="Ehtisham Abid">Ehtisham Abid</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><div>Icons made by <a href="https://www.flaticon.com/authors/iconpro86" title="Iconpro86">Iconpro86</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div><div>Icons made by <a href="https://www.flaticon.com/authors/iamkikirizky" title="Iamkikirizky">Iamkikirizky</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>


#application developed by Ariko John
print(platform)
print(primary_ext_storage)

kv_files = [
    "home.kv",
    "encode.kv",
    "decode.kv",

]

enc = EncodeMessage()

# class MainScreen(MDScreen):
#     pass


class HideMessageScreen(MDScreen):
    pass

class HideContent(MDBoxLayout):
    pass
    
   

class ExtractContent(MDBoxLayout):
    pass

class AboutContent(MDBoxLayout):
    pass

class CreditsContent(MDBoxLayout):
    pass

class StegnographyApp(MDApp):
    def _is_modern_dialog_api(self):
        return (
            MDDialogHeadlineText is not None
            and MDDialogSupportingText is not None
            and MDDialogButtonContainer is not None
            and MDDialogContentContainer is not None
        )

    def _build_custom_dialog(self, content_widget, title=None):
        if self._is_modern_dialog_api():
            dialog_parts = []
            if title:
                dialog_parts.append(MDDialogHeadlineText(text=str(title)))
            dialog_parts.append(
                MDDialogContentContainer(
                    content_widget,
                    orientation="vertical",
                )
            )
            return MDDialog(*dialog_parts)

        return MDDialog(type="custom", content_cls=content_widget)

    
    
    def __init__(self, **kwargs):
        super(StegnographyApp,self).__init__(**kwargs)
        self.theme_cls.theme_style = 'Dark'
        self.output_dir = (
            "/internal storage/android/encoded images/data"
            if platform == "android"
            else str(Path.home() / "Pictures")
        )
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.output_file_path = None
        self._update_dialog = None

    def on_start(self):
        self._request_android_permissions()
        Clock.schedule_once(lambda *_: self.check_for_updates_async(), 1.5)

    def _request_android_permissions(self):
        if platform != "android":
            return

        try:
            sdk_version = autoclass("android.os.Build$VERSION").SDK_INT
            permissions = [Permission.INTERNET]
            if sdk_version >= 33:
                permissions.append(Permission.READ_MEDIA_IMAGES)
            else:
                permissions.append(Permission.READ_EXTERNAL_STORAGE)

            request_permissions(permissions)
        except Exception as exc:
            self.show_dialog(f"Permission setup warning: {exc}")

    # def on_start(self):
    #     self.screen_manager.get_screen("setting").ids.storage_path.text = primary_ext_storage


    def show_dialog(self,text):
        if self._is_modern_dialog_api():
            dialog = MDDialog(
                MDDialogHeadlineText(text="Notice"),
                MDDialogSupportingText(text=str(text)),
                MDDialogButtonContainer(
                    MDWidget(),
                    make_dialog_button("OK", lambda *_: dialog.dismiss()),
                    spacing="8dp",
                ),
            )
            dialog.open()
            return

        # Legacy fallback for older KivyMD versions.
        dialog = MDDialog(text=str(text))
        dialog.open()

    def clear_input(self,input1):
        input1.text = ""
        # input2.text = ""


    def follow_us(self):
        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse('https://twitter.com/'))
            activity.startActivity(intent)

        except Exception as e:
            self.show_dialog(f"This feature only works for android version {e}")
            # https://github.com/ajohn256
    
    def follow_us_github(self):
        try:
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse('https://github.com/Arikorslan'))
            activity.startActivity(intent)

        except Exception as e:
            self.show_dialog(f"This feature only works for android version {e}")

    def select_image_to_encode(self):
        try:
            filechooser.open_file(on_selection=self.select_path)

        except Exception as e:
            print(e)

    def select_output_path_encode(self):
        try:
            if hasattr(filechooser, "save_file"):
                filechooser.save_file(on_selection=self.select_output_path)
            else:
                filechooser.open_file(on_selection=self.select_output_path)
        except Exception as e:
            print(e)
    
    def select_path(self, selection):
        
        try:
            if not selection:
                return
            print(selection)
            self.output_file_path = None
            notification.notify(title="Python-app", message=Path(selection[0]).stem)
            hide_screen = self.screen_manager.get_screen("hide_message_screen")
            hide_screen.ids.image_src.text = selection[0]
            if "output_path" in hide_screen.ids:
                hide_screen.ids.output_path.text = "Save location will appear here"
        
        except Exception as e:
            notification.notify(title="Python-app", message=str(e))

    def select_output_path(self, selection):
        try:
            if not selection:
                return
            chosen_path = Path(selection[0])
            self.output_file_path = str(chosen_path)
            hide_screen = self.screen_manager.get_screen("hide_message_screen")
            if "output_path" in hide_screen.ids:
                hide_screen.ids.output_path.text = str(chosen_path)
            notification.notify(title="Python-app", message=chosen_path.name or str(chosen_path))
        except Exception as e:
            notification.notify(title="Python-app", message=str(e))
       
    def exit_manager(self, *args):
        
        self.file_manager.close()

    
    def select_path_decode(self, path):
        
        try:
            if not path:
                return
            print(path)
            notification.notify(title="Python-app", message=Path(path[0]).stem)
            self.screen_manager.get_screen("extract_message_screen").ids.enc_img.text = path[0]

        
        except Exception as e:
            notification.notify(title="Python-app", message=str(e))

    def select_image_to_decode(self):
        try:
            filechooser.open_file(on_selection=self.select_path_decode)

        except Exception as e:
            print(e)
  
    def share_app(self):
        try:
            string = autoclass('java.lang.String')
            Intent = autoclass('android.content.Intent')
            sendIntent = Intent()
            sendIntent.setAction(Intent.ACTION_SEND)
            sendIntent.setType("text/plain")
            sendIntent.putExtra(Intent.EXTRA_TEXT, string("Hey there friend check out this application https://kivymd.readthedocs.io/en/latest/components/card"))
            sendIntent.setPackage("com.whatsapp")
            activity.startActivity(sendIntent)
        except Exception as e:
            self.show_dialog(f"This feature only works for android version {e}")
    
    def email_app(self):
        try:
            string = autoclass('java.lang.String')
            Intent = autoclass('android.content.Intent')
            sendIntent = Intent()
            sendIntent.setAction(Intent.ACTION_SEND)
            sendIntent.setType("text/plain")
            sendIntent.putExtra(Intent.EXTRA_TEXT, string())
            sendIntent.setPackage("com.google.android.gm")
            activity.startActivity(sendIntent)
        except Exception as e:
            self.show_dialog(f"This feature only works for android version {e}")
            
    def show_about(self):
        self.dialogabout = self._build_custom_dialog(AboutContent(), title="About")
        self.dialogabout.open()
    
    def show_credits(self):
        self.dialog = self._build_custom_dialog(CreditsContent(), title="Credits")
        self.dialog.open()

    def hide_message_dialog(self):
        self.dialog = self._build_custom_dialog(HideContent(), title="Set Password")
        self.dialog.open()
    
    def hide_message_(self,stop):
        
        try:
            if len(stop) < 4:
                self.dialog.dismiss()
                self.show_dialog("Please use a password with at least 4 characters.")
                return

            app_toast("Encoding message please wait...")
            image = self.screen_manager.get_screen('hide_message_screen').ids.image_src.text
            message = self.screen_manager.get_screen('hide_message_screen').ids.secret_message.text
            if not image:
                self.dialog.dismiss()
                self.show_dialog("Please select an image first.")
                return
            if not message:
                self.dialog.dismiss()
                self.show_dialog("Please enter a secret message first.")
                return

            output_path = enc.encode_message_(image, message, stop, self.output_dir, self.output_file_path)
            print("Done encoding")
            self.dialog.dismiss()
            self.show_dialog(f"Message encoded successfully.\nSaved at:\n{output_path}")
        
        except Exception as e:
            self.screen_manager.get_screen('hide_message_screen').ids.secret_message.text = "Unable to encode message into image"
            self.dialog.dismiss()
            self.show_dialog(str(e))
        


    
    def extract_message_dialog(self):
        self.dialog1 = self._build_custom_dialog(ExtractContent())
        

        self.dialog1.open()
    
    def extract_message(self,stop):
        
        
        try:
            if not stop:
                self.dialog1.dismiss()
                self.show_dialog("Please enter the password first.")
                return
            app_toast("Decoding message please wait.....")
            image = self.screen_manager.get_screen("extract_message_screen").ids.enc_img.text
            if not image:
                self.dialog1.dismiss()
                self.show_dialog("Please select an image first.")
                return
            
            resp = enc.decode_message(image,stop)
            self.screen_manager.get_screen("extract_message_screen").ids.decoded_message.text = resp

            self.dialog1.dismiss()
        
        except Exception as ex:
            print(ex)
            self.screen_manager.get_screen("extract_message_screen").ids.decoded_message.text = "Unable to decode message please ensure password is correct"
            self.show_dialog(str(ex))
            self.dialog1.dismiss()



        

 
    def change_screen(self,name):
        self.screen_manager.current = name
    

    def show_image(self,show_image):
        show_image.source = self.file[0]
        

    def build(self):
        self.screen_manager = ScreenManager()

        for file in kv_files:
            self.screen_manager.add_widget(Builder.load_file(file))


        return self.screen_manager

    def check_for_updates_async(self):
        worker = threading.Thread(target=self._check_for_updates_worker, daemon=True)
        worker.start()

    def _check_for_updates_worker(self):
        info = check_for_update()
        if info:
            Clock.schedule_once(lambda *_: self._show_update_dialog(info), 0)

    def _show_update_dialog(self, release_info):
        message = (
            f"New version available: {release_info['name']}\n"
            f"Current version: {APP_VERSION}\n\n"
            "Would you like to download the update now?"
        )

        if self._is_modern_dialog_api():
            self._update_dialog = MDDialog(
                MDDialogHeadlineText(text="Update available"),
                MDDialogSupportingText(text=message),
                MDDialogButtonContainer(
                    MDWidget(),
                    make_dialog_button("LATER", lambda *_: self._update_dialog.dismiss()),
                    make_dialog_button(
                        "DOWNLOAD",
                        lambda *_: self._open_update_link(
                            release_info.get("download_url") or release_info.get("html_url")
                        ),
                    ),
                    spacing="8dp",
                ),
            )
        else:
            self._update_dialog = MDDialog(
                title="Update available",
                text=message,
                buttons=[
                    make_dialog_button("LATER", lambda *_: self._update_dialog.dismiss()),
                    make_dialog_button(
                        "DOWNLOAD",
                        lambda *_: self._open_update_link(
                            release_info.get("download_url") or release_info.get("html_url")
                        ),
                    ),
                ],
            )
        self._update_dialog.open()

    def _open_update_link(self, url):
        if not url:
            if self._update_dialog:
                self._update_dialog.dismiss()
            self.show_dialog("No update URL found for this release.")
            return

        try:
            if platform == "android":
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(url))
                activity.startActivity(intent)
            else:
                import webbrowser

                webbrowser.open(url)
        except Exception as exc:
            self.show_dialog(f"Unable to open update link: {exc}")
        finally:
            if self._update_dialog:
                self._update_dialog.dismiss()


if __name__ == "__main__":
    StegnographyApp().run()