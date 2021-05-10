from src.facades.config import Config

class KucoinAdapter:
    @staticmethod
    def market_plug(market: str) -> str:
        market = market.upper()
        bases = Config.get('base-markets')
        for base in bases:
            base = base.upper()
            if market.endswith(base):
                return '{}-{}'.format(market[:-len(base)], base)
        return ''
