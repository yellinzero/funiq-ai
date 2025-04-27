import decimal
from abc import ABC, abstractmethod

from ..schemas import AIModelEntity, LLMUsage, PriceConfig, PriceInfo, PriceType


class PriceHandlingMixin(ABC):
    """Mixin class for handling price calculations for model usage."""

    @abstractmethod
    def get_model_schema(self, model: str) -> AIModelEntity | None:
        pass
    
    @abstractmethod
    def get_invoke_latency(self) -> float:
        pass
    
    def calculate_price(self, model: str, price_config: PriceConfig, price_type: PriceType, tokens: int) -> PriceInfo:
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

        # Calculate total amount with proper rounding
        total_amount = tokens * unit_price * price_config.unit
        total_amount = total_amount.quantize(decimal.Decimal("0.0000001"), rounding=decimal.ROUND_HALF_UP)

        return PriceInfo(
            unit_price=unit_price,
            unit=price_config.unit,
            total_amount=total_amount,
            currency=price_config.currency,
        )
       
    def _calc_response_usage(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> LLMUsage:
        """
        Calculate response usage

        :param model: model name
        :param credentials: model credentials
        :param prompt_tokens: prompt tokens
        :param completion_tokens: completion tokens
        :return: usage
        """
        # get prompt config
        schema = self.get_model_schema(model=model)
        
        if not schema:
            raise ValueError(f'No schema found for model: {model}')
        pricing = schema.pricing
        if not pricing:
            raise ValueError(f'No price info found for model: {model}')
        
        price_config = pricing[0]
        # get prompt price info
        prompt_price_info = self.calculate_price(
            model=model,
            price_config=price_config,
            price_type=PriceType.INPUT,
            tokens=prompt_tokens,
        )

        # get completion price info
        completion_price_info = self.calculate_price(
            model=model,
            price_config=price_config,
            price_type=PriceType.OUTPUT,
            tokens=completion_tokens,
        )

        # transform usage
        usage = LLMUsage(
            prompt_tokens=prompt_tokens,
            prompt_unit_price=prompt_price_info.unit_price,
            prompt_price_unit=prompt_price_info.unit,
            prompt_price=prompt_price_info.total_amount,
            completion_tokens=completion_tokens,
            completion_unit_price=completion_price_info.unit_price,
            completion_price_unit=completion_price_info.unit,
            completion_price=completion_price_info.total_amount,
            total_tokens=prompt_tokens + completion_tokens,
            total_price=prompt_price_info.total_amount + completion_price_info.total_amount,
            currency=prompt_price_info.currency,
            latency=self.get_invoke_latency(),
        )

        return usage