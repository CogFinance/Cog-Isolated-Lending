import { AnswerUpdated } from '../../generated/AccessControlledOffchainAggregator/AccessControlledOffchainAggregator'
import { updatePair } from '../entities/pair'


export function onAnswerUpdated(event: AnswerUpdated): void {
    // Update priced token prices
    updatePair(event.block.timestamp)
}