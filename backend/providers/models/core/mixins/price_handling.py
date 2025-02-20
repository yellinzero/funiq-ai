import decimal
from abc import ABC, abstractmethod
from collections.abc import Mapping

from ..models.model import AIModelEntity, PriceInfo, PriceType


class PriceHandling(ABC):
    """Mixin class for handling price calculations for model usage."""
    
    @property
    @abstractmethod
    def get_model_schema(self, model: str, credentials: Mapping | None = None) -> AIModelEntity | None:
        """Get the model schema containing pricing information.
        
        Args:
            model: Model identifier
            credentials: Optional model credentials
            
        Returns:
            AIModelEntity if found, None otherwise
        """
        raise NotImplementedError

    def calculate_price(self, model: str, credentials: dict, price_type: PriceType, tokens: int) -> PriceInfo:
        """
        Calculate price for given model usage.

        Args:
            model: Model identifier
            credentials: Model credentials
            price_type: Type of pricing (input/output)
            tokens: Number of tokens to calculate price for
            
        Returns:
            PriceInfo containing unit price, units, total amount and currency
            
        Raises:
            ValueError: If price configuration is not found for the model
        """
        # Get model schema and pricing config
        model_schema = self.get_model_schema(model, credentials)
        price_config = model_schema.pricing if model_schema else None

        # Get unit price based on price type
        unit_price = None
        if price_config:
            unit_price = (
                price_config.input if price_type == PriceType.INPUT
                else price_config.output if price_type == PriceType.OUTPUT
                else None
            )

        # Return zero price if no unit price found
        if unit_price is None:
            return PriceInfo(
                unit_price=decimal.Decimal("0.0"),
                unit=decimal.Decimal("0.0"), 
                total_amount=decimal.Decimal("0.0"),
                currency="USD",
            )

        if not price_config:
            raise ValueError(f"Price configuration not found for model {model}")

        # Calculate total amount with proper rounding
        total_amount = tokens * unit_price * price_config.unit
        total_amount = total_amount.quantize(decimal.Decimal("0.0000001"), rounding=decimal.ROUND_HALF_UP)

        return PriceInfo(
            unit_price=unit_price,
            unit=price_config.unit,
            total_amount=total_amount,
            currency=price_config.currency,
        )