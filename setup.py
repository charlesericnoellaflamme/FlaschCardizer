import cx_Freeze
import sys

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("FlashCardizer.py", base=base, icon="media/Icon.ico")]

cx_Freeze.setup(
    name="FlashCardizerClient",
    options={"build_exe": {"packages": ["tkinter", "pdf2image", "PIL"], "include_files": ["media/BlurCard.png",
                                                                                          "media/BlurSelection.png",
                                                                                          "media/BlurSlider.png",
                                                                                          "media/ClearCard.png",
                                                                                          "media/ClearSelection.png",
                                                                                          "media/ColorCard.png",
                                                                                          "media/ColorSelection.png",
                                                                                          "media/Delete.png",
                                                                                          "media/Edit.png",
                                                                                          "media/Icon.ico",
                                                                                          "media/ImportPdf.png",
                                                                                          "media/LoadCards.png",
                                                                                          "media/Loading.gif",
                                                                                          "media/Lock.png",
                                                                                          "media/Logo.png",
                                                                                          "media/Next.png",
                                                                                          "media/PageCorner.png",
                                                                                          "media/PageCornerBack.png",
                                                                                          "media/PageCornerFront.png",
                                                                                          "media/Previous.png",
                                                                                          "media/Slider.png",
                                                                                          "media/Study.png",
                                                                                          "media/Unlock.png",
                                                                                          "media/Void.png"]}},
    version="1.0",
    description="FlashCardizer: A Flashcard Building Application",
    executables=executables
    )

