import { AnswerUpdated } from '../../generated/AccessControlledOffchainAggregator/AccessControlledOffchainAggregator'
import { updateToken } from '../entities/token'


export function onAnswerUpdated(event: AnswerUpdated): void {
    // Update priced token prices
    updateToken(event.block.timestamp)
}