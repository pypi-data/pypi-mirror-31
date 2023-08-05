from typing import Callable, Dict, Iterator, Sequence, Union

from PyQt5.QtWidgets import QWidget

from groot_gui.forms.resources import resources

from groot.constants import EIntent, LegoStage, STAGES
from intermake import Plugin
from mhelper import array_helper


TWorkflows = Union[LegoStage, Sequence[LegoStage]]
TAction = Union["FrmBase", QWidget, Plugin, Callable[[], None]]


class LegoVisualiser:
    
    
    def __init__( self, name: str, action: TAction, *, view: TWorkflows = (), create: TWorkflows = (), drop: TWorkflows = (), icon = None, key: str = None ):
        self.name = name
        self.action = action
        self.intents: Dict[EIntent, Sequence[LegoStage]] = { }
        self.intents[EIntent.VIEW] = array_helper.as_sequence( view )
        self.intents[EIntent.CREATE] = array_helper.as_sequence( create )
        self.intents[EIntent.DROP] = array_helper.as_sequence( drop )
        self.icon = icon
        self.key = key
    
    
    def __str__( self ):
        return self.key or "{{No key, name = {}}}".format( self.name )
    
    
    @property
    def is_visible( self ):
        from groot_gui.forms.frm_base import FrmBase
        if isinstance( self.action, type ) and issubclass( self.action, FrmBase ):
            from groot_gui.forms.frm_main import FrmMain
            return self.action.__name__ in FrmMain.INSTANCE.mdi
        else:
            return False
        
    @staticmethod
    def for_stage(stage:LegoStage, intent:EIntent):
        for visualiser in VISUALISERS:
            if stage in visualiser.intents[intent]:
                yield visualiser


class LegoVisualiserCollection:
    def __init__( self ):
        from groot_gui.forms.frm_lego import FrmLego
        from groot_gui.forms.frm_alignment import FrmAlignment
        from groot_gui.forms.frm_webtree import FrmWebtree
        from groot_gui.forms.frm_fusions import FrmFusions
        from groot_gui.forms.frm_view_splits import FrmViewSplits
        from groot_gui.forms.frm_samples import FrmLoadFile
        from groot_gui.forms.frm_samples import FrmSaveFile
        from groot_gui.forms.frm_startup import FrmStartup
        from groot_gui.forms.frm_debug import FrmDebug
        from groot_gui.forms.frm_view_options import FrmViewOptions
        from groot_gui.forms.frm_workflow import FrmWorkflow
        from groot_gui.forms.frm_wizard import FrmWizard
        from groot_gui.utilities.gui_actions import GuiActions
        from groot_gui.forms.frm_run_algorithm import FrmCreateSubgraphs, FrmCreateAlignment, FrmCreateDomains, FrmCreateTrees
        from groot_gui.forms.frm_about import FrmAbout
        import groot
        
        
        # Workflow viewing
        self.VIEW_TEXT = LegoVisualiser( "Report", FrmWebtree, view = (STAGES.FASTA_1,
                                                                       STAGES.BLAST_2,
                                                                       STAGES.MAJOR_3,
                                                                       STAGES.MINOR_3,
                                                                       STAGES.DOMAINS_4,
                                                                       STAGES.ALIGNMENTS_5,
                                                                       STAGES.TREES_6,
                                                                       STAGES.FUSIONS_7,
                                                                       STAGES.SPLITS_8,
                                                                       STAGES.CONSENSUS_9,
                                                                       STAGES.SUBSETS_10,
                                                                       STAGES.PREGRAPHS_11,
                                                                       STAGES.SUBGRAPHS_11,
                                                                       STAGES.FUSED_12,
                                                                       STAGES.CLEANED_13,
                                                                       STAGES.CHECKED_14), icon = resources.text, key = "view_trees" )
        self.VIEW_LEGO = LegoVisualiser( "Lego", FrmLego, view = (STAGES.FASTA_1,
                                                                  STAGES.BLAST_2,
                                                                  STAGES.MAJOR_3,
                                                                  STAGES.MINOR_3,
                                                                  STAGES.DOMAINS_4), icon = resources.lego, key = "view_lego" )
        self.VIEW_ALIGNMENT = LegoVisualiser( "Alignment", FrmAlignment, view = (STAGES.FASTA_1, STAGES.MINOR_3, STAGES.ALIGNMENTS_5), icon = resources.align, key = "view_alignments" )
        self.VIEW_FUSIONS = LegoVisualiser( "Fusions", FrmFusions, view = STAGES.FUSIONS_7, icon = resources.fusion )
        self.VIEW_SPLITS = LegoVisualiser( "Splits", FrmViewSplits, view = (STAGES.FASTA_1, STAGES.MAJOR_3, STAGES.SPLITS_8, STAGES.CONSENSUS_9), icon = resources.split )
        self.VIEW_OPEN_FILE = LegoVisualiser( "Browse open", FrmLoadFile, icon = resources.open, key = "view_open_file" )
        self.VIEW_SAVE_FILE = LegoVisualiser( "Browse save", FrmSaveFile, icon = resources.save )
        self.VIEW_DEBUG = LegoVisualiser( "Debug", FrmDebug )
        
        # Creating
        self.CREATE_BLAST_FASTA = LegoVisualiser( "Import file", GuiActions.import_file, create = (STAGES.FASTA_1, STAGES.BLAST_2), icon = resources.create, key = "import_file" )
        self.CREATE_MAJOR = LegoVisualiser( "Create major", groot.create_major, create = STAGES.MAJOR_3, icon = resources.create, key = "create_major" )
        self.CREATE_MINOR = LegoVisualiser( "Create minor", groot.create_minor, create = STAGES.MINOR_3, icon = resources.create )
        self.CREATE_DOMAINS = LegoVisualiser( "Create domains", FrmCreateDomains, view = STAGES.DOMAINS_4, create = STAGES.DOMAINS_4, drop = STAGES.DOMAINS_4, icon = resources.create, key = "view_domains" )
        self.CREATE_ALIGNMENTS = LegoVisualiser( "Create alignments", FrmCreateAlignment, create = STAGES.ALIGNMENTS_5, icon = resources.create, key = "create_alignments" )
        self.CREATE_TREES = LegoVisualiser( "Create trees", FrmCreateTrees, create = STAGES.TREES_6, icon = resources.create, key = "create_trees" )
        self.CREATE_FUSIONS = LegoVisualiser( "Create fusions", groot.create_fusions, create = STAGES.FUSIONS_7, icon = resources.create, key = "create_fusions" )
        self.CREATE_SPLITS = LegoVisualiser( "Create splits", groot.create_splits, create = STAGES.SPLITS_8, icon = resources.create )
        self.CREATE_CONSENSUS = LegoVisualiser( "Create consensus", groot.create_consensus, create = STAGES.CONSENSUS_9, icon = resources.create )
        self.CREATE_SUBSETS = LegoVisualiser( "Create subsets", groot.create_subsets, create = STAGES.SUBSETS_10, icon = resources.create, key = "create_subsets" )
        self.CREATE_PREGRAPHS = LegoVisualiser( "Create pregraphs", groot.create_pregraphs, create = STAGES.PREGRAPHS_11, icon = resources.create )
        self.CREATE_SUBGRAPHS = LegoVisualiser( "Create subgraphs", FrmCreateSubgraphs, create = STAGES.SUBGRAPHS_11, icon = resources.create, key = "create_subgraphs" )
        self.CREATE_FUSED = LegoVisualiser( "Create fused", groot.create_fused, create = STAGES.FUSED_12, icon = resources.create, key = "create_fused" )
        self.CREATE_CLEANED = LegoVisualiser( "Create cleaned", groot.create_cleaned, create = STAGES.CLEANED_13, icon = resources.create )
        self.CREATE_CHECKED = LegoVisualiser( "Create checked", groot.create_checked, create = STAGES.CHECKED_14, icon = resources.create )
        
        # Dropping
        self.DROP_MAJOR = LegoVisualiser( "Drop major", groot.drop_components, drop = STAGES.MAJOR_3, icon = resources.remove )
        self.DROP_MINOR = LegoVisualiser( "Drop minor", groot.drop_components, drop = STAGES.MINOR_3, icon = resources.remove )
        self.DROP_ALIGNMENTS = LegoVisualiser( "Drop alignments", groot.drop_alignment, drop = STAGES.ALIGNMENTS_5, icon = resources.remove, key = "drop_alignments" )
        self.DROP_TREES = LegoVisualiser( "Drop trees", groot.drop_tree, drop = STAGES.TREES_6, icon = resources.remove, key = "drop_trees" )
        self.DROP_FUSIONS = LegoVisualiser( "Drop fusions", groot.drop_fusions, drop = STAGES.FUSIONS_7, icon = resources.remove )
        self.DROP_CANDIDATES = LegoVisualiser( "Drop splits", groot.drop_splits, drop = STAGES.SPLITS_8, icon = resources.remove )
        self.DROP_VIABLE = LegoVisualiser( "Drop consensus", groot.drop_consensus, drop = STAGES.CONSENSUS_9, icon = resources.remove )
        self.DROP_SUBSETS = LegoVisualiser( "Drop subsets", groot.drop_subsets, drop = STAGES.SUBSETS_10, icon = resources.remove )
        self.DROP_PREGRAPHS = LegoVisualiser( "Drop pregraphs", groot.drop_pregraphs, drop = STAGES.PREGRAPHS_11, icon = resources.remove, key = "drop_subgraphs" )
        self.DROP_SUBGRAPHS = LegoVisualiser( "Drop subgraphs", groot.drop_supertrees, drop = STAGES.SUBGRAPHS_11, icon = resources.remove, key = "drop_subgraphs" )
        self.DROP_FUSED = LegoVisualiser( "Drop fused", groot.drop_fused, drop = STAGES.FUSED_12, icon = resources.remove )
        self.DROP_CLEANED = LegoVisualiser( "Drop cleaned", groot.drop_cleaned, drop = STAGES.CLEANED_13, icon = resources.remove )
        self.DROP_CHECKED = LegoVisualiser( "Drop checked", groot.drop_checked, drop = STAGES.CHECKED_14, icon = resources.remove )
        
        # Actions
        self.ACT_FILE_NEW = LegoVisualiser( "New", groot.file_new, icon = resources.new, key = "new_model" )
        self.ACT_FILE_SAVE = LegoVisualiser( "Save", GuiActions.save_model, icon = resources.save )
        self.ACT_FILE_SAVE_AS = LegoVisualiser( "Save as", GuiActions.browse_save, key = "file_save_as" )
        self.ACT_FILE_OPEN = LegoVisualiser( "Open", GuiActions.browse_open, key = "file_open" )
        self.ACT_FILE_SAVE_TO = LegoVisualiser( "Save file (x)", GuiActions.save_model_to, key = "save_file_to" )
        self.ACT_FILE_LOAD_FROM = LegoVisualiser( "Load file (x)", GuiActions.load_file_from, key = "load_file_from" )
        self.ACT_FILE_SAMPLE_FROM = LegoVisualiser( "Load sample (x)", GuiActions.load_sample_from, key = "load_sample_from" )
        self.ACT_EXIT = LegoVisualiser( "Exit", GuiActions.exit )
        self.ACT_STOP_WIZARD = LegoVisualiser( "Stop wizard", GuiActions.stop_wizard, key = "stop_wizard" )
        self.ACT_WIZARD_NEXT = LegoVisualiser( "Continue wizard", GuiActions.wizard_next, key = "wizard_next" )
        self.ACT_1 = LegoVisualiser( "Enable inbuilt browser", GuiActions.enable_inbuilt_browser, key = "enable_inbuilt_browser" )
        self.ACT_2 = LegoVisualiser( "dismiss_startup_screen", GuiActions.dismiss_startup_screen, key = "dismiss_startup_screen" )
        self.ACT_SELECT_MENU = LegoVisualiser( "Show selection", GuiActions.show_selection, key = "show_selection" )
        
        # Miscellaneous views
        self.VIEW_STARTUP = LegoVisualiser( "Startup", FrmStartup )
        self.VIEW_PREFERENCES = LegoVisualiser( "Preferences", FrmViewOptions, key = "view_options", icon = resources.settings )
        self.VIEW_WORKFLOW = LegoVisualiser( "Workflow", FrmWorkflow, icon = resources.workflow, key = "view_workflow" )
        self.VIEW_WIZARD = LegoVisualiser( "Wizard", FrmWizard, icon = resources.wizard, key = "view_wizard" )
        self.VIEW_ABOUT = LegoVisualiser( "About", FrmAbout, icon = resources.groot_logo )
        self.VIEW_HELP = LegoVisualiser( "Help", GuiActions.show_help, icon = resources.help_cursor, key = "view_help" )
        self.VIEW_INTERMAKE = LegoVisualiser( "Intermake", GuiActions.show_intermake )
    
    
    def __iter__( self ) -> Iterator[LegoVisualiser]:
        for v in self.__dict__.values():
            if isinstance( v, LegoVisualiser ):
                yield v
    
    
    def find_by_key( self, key: str ) -> LegoVisualiser:
        for item in self:
            if item.key == key:
                return item
        
        raise KeyError( key )


VISUALISERS: LegoVisualiserCollection = None


def init():
    global VISUALISERS
    
    if VISUALISERS is None:
        VISUALISERS = LegoVisualiserCollection()
