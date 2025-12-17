ClipboardPro/              <-- 根目录
│
├── main.py                # [启动口] 放在最外面
│
├── core/                  # [核心层] 放配置、工具、常量
│   ├── __init__.py        # (新建一个空文件，名字必须叫这个)
│   └── shared.py          # (原 ui_shared.py)
│
├── data/                  # [数据层] 放数据库相关
│   ├── __init__.py        # (空文件)
│   └── database.py        # (原 database.py)
│
├── services/              # [服务层] 放后台逻辑
│   ├── __init__.py        # (空文件)
│   └── clipboard.py       # (原 clipboard_manager.py)
│
└── ui/                    # [界面层] 放所有窗口代码
    ├── __init__.py        # (空文件)
    ├── main_window.py     # (原 ui_main.py)
    ├── components.py      # (原 ui_components.py)
    ├── panels.py          # (原 ui_panels.py)
    └── dialogs.py         # (原 ui_dialogs.py)
	
# ===================|===================

1. "未标签" 所谓的"未标签" 意思就是只能包含没有被标签绑定的数据, 凡是任何一条数据被绑定标签后, 就不能出现"未标签"的区里

# ===================|===================

1. 当按下空格键预览图片之后再次按下空格键时, 理应关闭窗口的, 但是却错误的触发了"坐旋转"按钮了

针对整个应用程序的界面, 你认为该使用多少种颜色呢?

来自内联样式 (12 种)是更新后的版本里的内联样式吗?