from tensorboardX import SummaryWriter

from torchtools import TRAIN_MODE
from torchtools.callbacks import Callback
from torchtools.meters import EPOCH_RESET, BATCH_RESET


class TensorBoardLogger(Callback):
    def __init__(self, log_dir=None, ignores=None, log_model_graph=False,
                 log_param_interval=0, *args, **kwargs):
        super(TensorBoardLogger, self).__init__(*args, **kwargs)
        self.writer = SummaryWriter(log_dir)
        if ignores is None:
            ignores = []
        self.ignores = ignores
        self.log_model_graph = log_model_graph
        self.log_param_interval = log_param_interval
        self.epochs_since_logged_params = 0

    def _teardown(self):
        self.writer.close()

    def log(self, step, meter):
        log_type = meter.meter_type
        method = getattr(self, 'log_' + log_type, None)
        if not method:
            return
        method(meter.alias, meter.value, step)

    def log_image(self, tag, img_tensor, step=None):
        self.board.add_image(tag, img_tensor, step)

    def log_scalar(self, tag, scalar_value, step=None):
        self.board.add_scalar(tag, scalar_value, step)

    def log_graph(self, model, input):
        self.board.add_graph(model, input)

    def log_hist(self, tag, value, step=None, bins='tensorflow'):
        self.board.add_histogram(tag, value, step, bins)

    def log_text(self):
        pass

    def log_audio(self):
        pass

    def _log_model_and_params(self, trainer, state):
        if state['mode'] != TRAIN_MODE:
            return

        if self.log_model_graph:
            model = state['model']
            input = state['input']
            self.log_graph(model, input)
            self.log_model_graph = False

        if self.log_param_interval == 0:
            return

        self.epochs_since_logged_params += 1
        if self.epochs_since_logged_params < self.log_param_interval:
            return
        self.epochs_since_logged_params = 0

        model = state['model']
        epochs = state['epochs']
        for name, params in model.named_parameters():
            self.log_hist(name, params.clone().cpu().data.numpy(), epochs)

    def __on_batch_end(self, trainer, state):
        """Deprecated"""
        iters = state['iters']
        mode = state['mode']
        for name, meter in state['meters'].items():
            if meter.meter_mode != mode:
                continue
            if meter.reset_mode == BATCH_RESET and \
                    name not in self.ignores and meter.can_call:
                self.log(iters, meter)

    def on_epoch_end(self, trainer, state):
        self._log_model_and_params(trainer, state)

        epochs = state['epochs']
        mode = state['mode']
        for meter in state['meters'].values():
            if meter.mode != mode:
                continue
            alias = meter.alias
            if (meter.reset_mode == EPOCH_RESET and
                    alias not in self.ignores):
                self.log(epochs, meter)

    def on_validate_end(self, trainer, state):
        self.on_epoch_end(trainer, state)
